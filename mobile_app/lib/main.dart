import 'dart:async';
import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:web_socket_channel/web_socket_channel.dart';

void main() {
  runApp(const ParkingApp());
}

class ParkingApp extends StatelessWidget {
  const ParkingApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'ParkFlow AI',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        useMaterial3: true,
        brightness: Brightness.dark,
        scaffoldBackgroundColor: const Color(0xFF07111F),
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF35A7FF),
          brightness: Brightness.dark,
        ),
      ),
      home: const ParkingHomePage(),
    );
  }
}

class ParkingHomePage extends StatefulWidget {
  const ParkingHomePage({super.key});

  @override
  State<ParkingHomePage> createState() => _ParkingHomePageState();
}

class _ParkingHomePageState extends State<ParkingHomePage> {
  static const String baseUrl =
      'http://192.168.1.4:8000';

  static const String recommendationWsUrl =
      'ws://192.168.1.4:8000/ws/recommendations';

  int _selectedTab = 0;

  Timer? _pollTimer;
  Timer? _reconnectTimer;

  WebSocketChannel? _recommendationChannel;

  final TextEditingController _vehicleController =
      TextEditingController(
    text: 'TN03EF9012',
  );

  bool _loading = true;
  bool _backendOnline = false;
  bool _cameraOnline = false;
  bool _visionRunning = false;

  String _lastUpdated = '--';

  int _totalSpaces = 0;
  int _occupiedSpaces = 0;
  int _availableSpaces = 0;
  double _occupancyPercentage = 0;

  int _activeVehicles = 0;
  int _totalEntries = 0;
  int _totalExits = 0;

  Map<String, bool> _parkingSpaces = {};

  Map<String, dynamic>? _recommendedExit;
  List<dynamic> _alternativeExits = [];

  List<dynamic> _exits = [];

  Map<String, dynamic>? _vehicleRoute;

  bool _routeLoading = false;

  final List<String> _alerts = [];

  @override
  void initState() {
    super.initState();

    _loadDashboard();

    _pollTimer = Timer.periodic(
      const Duration(seconds: 5),
      (_) {
        _loadDashboard();
      },
    );

    _connectRecommendationWebSocket();
  }

  @override
  void dispose() {
    _pollTimer?.cancel();
    _reconnectTimer?.cancel();

    _recommendationChannel?.sink.close();

    _vehicleController.dispose();

    super.dispose();
  }

  Future<dynamic> _get(String endpoint) async {
    final response = await http
        .get(
          Uri.parse('$baseUrl$endpoint'),
        )
        .timeout(
          const Duration(seconds: 10),
        );

    if (response.statusCode < 200 ||
        response.statusCode >= 300) {
      throw Exception(
        'HTTP ${response.statusCode}',
      );
    }

    return jsonDecode(response.body);
  }

  Future<void> _loadDashboard() async {
    try {
      final results = await Future.wait([
        _get('/api/vision/status'),
        _get('/api/vision/camera/status'),
        _get('/api/recommendations/'),
        _get('/api/exits/'),
      ]);

      final visionStatus =
          results[0] as Map<String, dynamic>;

      final cameraStatus =
          results[1] as Map<String, dynamic>;

      final recommendation =
          results[2] as Map<String, dynamic>;

      final exits =
          results[3] as List<dynamic>;

      final parkingVision =
          visionStatus['parking_vision']
              as Map<String, dynamic>?;

      final occupancy =
          parkingVision?['occupancy']
              as Map<String, dynamic>?;

      final tracking =
          parkingVision?['vehicle_tracking']
              as Map<String, dynamic>?;

      final visionAi =
          visionStatus['vision_ai']
              as Map<String, dynamic>?;

      final recommended =
          recommendation['recommended_exit']
              as Map<String, dynamic>?;

      final alternatives =
          recommendation['alternatives']
              as List<dynamic>?;

      final rawSpaces =
          occupancy?['spaces']
              as Map<String, dynamic>?;

      final parsedSpaces =
          <String, bool>{};

      if (rawSpaces != null) {
        for (final entry in rawSpaces.entries) {
          parsedSpaces[entry.key] =
              entry.value == true;
        }
      }

      _updateAlerts(exits);

      if (!mounted) return;

      setState(() {
        _loading = false;

        _backendOnline = true;

        _cameraOnline =
            cameraStatus['camera'] == 'ONLINE';

        _visionRunning =
            visionAi?['running'] == true;

        _totalSpaces =
            _toInt(
          occupancy?['total_spaces'],
        );

        _occupiedSpaces =
            _toInt(
          occupancy?['occupied_spaces'],
        );

        _availableSpaces =
            _toInt(
          occupancy?['available_spaces'],
        );

        _occupancyPercentage =
            _toDouble(
          occupancy?['occupancy_percentage'],
        );

        _activeVehicles =
            _toInt(
          tracking?['active_vehicles'],
        );

        _totalEntries =
            _toInt(
          tracking?['total_entries'],
        );

        _totalExits =
            _toInt(
          tracking?['total_exits'],
        );

        _parkingSpaces = parsedSpaces;

        _recommendedExit = recommended;

        _alternativeExits =
            alternatives ?? [];

        _exits = exits;

        _lastUpdated =
            _formatTime(
          DateTime.now(),
        );
      });
    } catch (_) {
      if (!mounted) return;

      setState(() {
        _loading = false;
        _backendOnline = false;
      });
    }
  }

  void _updateAlerts(List<dynamic> exits) {
    _alerts.clear();

    for (final exit in exits) {
      if (exit is! Map) {
        continue;
      }

      final name =
          exit['name']?.toString() ?? 'Exit';

      final available =
          exit['is_available'] == true;

      final congestion =
          exit['congestion_level']
                  ?.toString() ??
              'LOW';

      if (!available) {
        _alerts.add(
          '🚨 $name is currently blocked.',
        );
      } else if (congestion == 'HIGH') {
        _alerts.add(
          '⚠ $name has HIGH congestion.',
        );
      } else if (congestion == 'MEDIUM') {
        _alerts.add(
          '⚠ $name has MEDIUM congestion.',
        );
      }
    }

    if (_alerts.isEmpty) {
      _alerts.add(
        '✅ No active parking alerts.',
      );
    }
  }

  void _connectRecommendationWebSocket() {
    try {
      _recommendationChannel =
          WebSocketChannel.connect(
        Uri.parse(
          recommendationWsUrl,
        ),
      );

      _recommendationChannel!.stream.listen(
        (message) {
          try {
            final decoded =
                jsonDecode(message);

            if (decoded is! Map) {
              return;
            }

            if (decoded['type'] !=
                'AI_EXIT_RECOMMENDATION') {
              return;
            }

            final data =
                decoded['data'];

            if (data is! Map) {
              return;
            }

            final recommended =
                data['recommended_exit'];

            final alternatives =
                data['alternative_exits'] ??
                    data['alternatives'] ??
                    [];

            if (!mounted) return;

            setState(() {
              if (recommended is Map) {
                _recommendedExit =
                    Map<String, dynamic>.from(
                  recommended,
                );
              }

              if (alternatives is List) {
                _alternativeExits =
                    alternatives;
              }

              _lastUpdated =
                  _formatTime(
                DateTime.now(),
              );
            });
          } catch (_) {
            // Ignore malformed messages.
          }
        },
        onError: (_) {
          _scheduleWebSocketReconnect();
        },
        onDone: () {
          _scheduleWebSocketReconnect();
        },
      );
    } catch (_) {
      _scheduleWebSocketReconnect();
    }
  }

  void _scheduleWebSocketReconnect() {
    _reconnectTimer?.cancel();

    _reconnectTimer = Timer(
      const Duration(seconds: 5),
      _connectRecommendationWebSocket,
    );
  }

  Future<void> _loadVehicleRoute() async {
    final vehicle =
        _vehicleController.text.trim();

    if (vehicle.isEmpty) {
      _showMessage(
        'Enter a vehicle number.',
      );
      return;
    }

    setState(() {
      _routeLoading = true;
      _vehicleRoute = null;
    });

    try {
      final result =
          await _get(
        '/api/routes/$vehicle',
      );

      if (!mounted) return;

      setState(() {
        _vehicleRoute =
            Map<String, dynamic>.from(
          result as Map,
        );

        _routeLoading = false;

        _selectedTab = 2;
      });
    } catch (_) {
      if (!mounted) return;

      setState(() {
        _routeLoading = false;
      });

      _showMessage(
        'Unable to calculate the route.',
      );
    }
  }

  void _showMessage(String text) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(text),
        behavior: SnackBarBehavior.floating,
      ),
    );
  }

  int _toInt(dynamic value) {
    if (value is int) {
      return value;
    }

    if (value is num) {
      return value.toInt();
    }

    return int.tryParse(
          value?.toString() ?? '',
        ) ??
        0;
  }

  double _toDouble(dynamic value) {
    if (value is double) {
      return value;
    }

    if (value is num) {
      return value.toDouble();
    }

    return double.tryParse(
          value?.toString() ?? '',
        ) ??
        0.0;
  }

  String _formatTime(DateTime time) {
    final hour =
        time.hour.toString().padLeft(2, '0');

    final minute =
        time.minute.toString().padLeft(2, '0');

    final second =
        time.second.toString().padLeft(2, '0');

    return '$hour:$minute:$second';
  }

  Color _congestionColor(String value) {
    switch (value.toUpperCase()) {
      case 'HIGH':
        return Colors.redAccent;

      case 'MEDIUM':
        return Colors.orangeAccent;

      default:
        return Colors.greenAccent;
    }
  }

  Color _availabilityColor(bool available) {
    return available
        ? Colors.greenAccent
        : Colors.redAccent;
  }

  Widget _glassCard({
    required Widget child,
    EdgeInsets padding =
        const EdgeInsets.all(18),
  }) {
    return Container(
      width: double.infinity,
      padding: padding,
      decoration: BoxDecoration(
        color: const Color(0xFF101D31),
        borderRadius:
            BorderRadius.circular(24),
        border: Border.all(
          color: Colors.white.withAlpha(18),
        ),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withAlpha(40),
            blurRadius: 16,
            offset: const Offset(0, 8),
          ),
        ],
      ),
      child: child,
    );
  }

  Widget _statusDot(bool active) {
    return Container(
      width: 9,
      height: 9,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        color: active
            ? Colors.greenAccent
            : Colors.redAccent,
        boxShadow: [
          BoxShadow(
            color: active
                ? Colors.greenAccent.withAlpha(90)
                : Colors.redAccent.withAlpha(90),
            blurRadius: 8,
          ),
        ],
      ),
    );
  }

  Widget _statusPill({
    required String label,
    required bool active,
  }) {
    final color = active
        ? Colors.greenAccent
        : Colors.redAccent;

    return Container(
      padding:
          const EdgeInsets.symmetric(
        horizontal: 12,
        vertical: 8,
      ),
      decoration: BoxDecoration(
        color: color.withAlpha(18),
        borderRadius:
            BorderRadius.circular(14),
        border: Border.all(
          color: color.withAlpha(75),
        ),
      ),
      child: Row(
        mainAxisSize:
            MainAxisSize.min,
        children: [
          _statusDot(active),
          const SizedBox(width: 7),
          Text(
            label,
            style: TextStyle(
              color: color,
              fontWeight:
                  FontWeight.w700,
              fontSize: 12,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildHeader() {
    return Row(
      children: [
        Container(
          width: 50,
          height: 50,
          decoration: BoxDecoration(
            gradient:
                const LinearGradient(
              colors: [
                Color(0xFF36A7FF),
                Color(0xFF7067FF),
              ],
            ),
            borderRadius:
                BorderRadius.circular(16),
          ),
          child: const Icon(
            Icons.local_parking_rounded,
            color: Colors.white,
            size: 27,
          ),
        ),
        const SizedBox(width: 13),
        Expanded(
          child: Column(
            crossAxisAlignment:
                CrossAxisAlignment.start,
            children: [
              const Text(
                'PARKFLOW AI',
                style: TextStyle(
                  fontSize: 20,
                  fontWeight:
                      FontWeight.w900,
                  letterSpacing: 1.3,
                ),
              ),
              Text(
                'Smart parking control',
                style: TextStyle(
                  fontSize: 12,
                  color: Colors.white.withAlpha(145),
                ),
              ),
            ],
          ),
        ),
        IconButton(
          onPressed: _loadDashboard,
          icon: const Icon(
            Icons.refresh_rounded,
          ),
        ),
      ],
    );
  }

  Widget _buildLiveStatusRow() {
    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      child: Row(
        children: [
          _statusPill(
            label: 'BACKEND',
            active: _backendOnline,
          ),
          const SizedBox(width: 8),
          _statusPill(
            label: 'CAMERA',
            active: _cameraOnline,
          ),
          const SizedBox(width: 8),
          _statusPill(
            label: 'AI ENGINE',
            active: _visionRunning,
          ),
          const SizedBox(width: 8),
          Container(
            padding:
                const EdgeInsets.symmetric(
              horizontal: 12,
              vertical: 8,
            ),
            decoration: BoxDecoration(
              color: Colors.blueAccent
                  .withAlpha(18),
              borderRadius:
                  BorderRadius.circular(14),
            ),
            child: Text(
              'Updated $_lastUpdated',
              style: const TextStyle(
                fontSize: 11,
                color: Colors.white70,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildOccupancyHero() {
    final progress =
        (_occupancyPercentage / 100)
            .clamp(0.0, 1.0);

    return _glassCard(
      padding:
          const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment:
            CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Expanded(
                child: Text(
                  'LIVE OCCUPANCY',
                  style: TextStyle(
                    fontWeight:
                        FontWeight.w800,
                    letterSpacing: 1,
                    color: Colors.white70,
                  ),
                ),
              ),
              Container(
                padding:
                    const EdgeInsets.symmetric(
                  horizontal: 10,
                  vertical: 6,
                ),
                decoration: BoxDecoration(
                  color: Colors.greenAccent
                      .withAlpha(15),
                  borderRadius:
                      BorderRadius.circular(10),
                ),
                child: const Text(
                  'LIVE',
                  style: TextStyle(
                    fontSize: 10,
                    fontWeight:
                        FontWeight.bold,
                    color: Colors.greenAccent,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 18),
          Row(
            children: [
              SizedBox(
                width: 126,
                height: 126,
                child: Stack(
                  alignment: Alignment.center,
                  children: [
                    SizedBox(
                      width: 126,
                      height: 126,
                      child:
                          CircularProgressIndicator(
                        value: progress,
                        strokeWidth: 12,
                        backgroundColor:
                            Colors.white10,
                        color:
                            Colors.cyanAccent,
                      ),
                    ),
                    Column(
                      mainAxisAlignment:
                          MainAxisAlignment.center,
                      children: [
                        Text(
                          '${_occupancyPercentage.toStringAsFixed(0)}%',
                          style:
                              const TextStyle(
                            fontSize: 28,
                            fontWeight:
                                FontWeight.w900,
                          ),
                        ),
                        const Text(
                          'used',
                          style:
                              TextStyle(
                            fontSize: 11,
                            color:
                                Colors.white60,
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
              const SizedBox(width: 20),
              Expanded(
                child: Column(
                  crossAxisAlignment:
                      CrossAxisAlignment.start,
                  children: [
                    _metricLine(
                      'Total Spaces',
                      '$_totalSpaces',
                      Icons.grid_view_rounded,
                    ),
                    _metricLine(
                      'Occupied',
                      '$_occupiedSpaces',
                      Icons.directions_car_filled,
                    ),
                    _metricLine(
                      'Available',
                      '$_availableSpaces',
                      Icons.check_circle_outline,
                    ),
                  ],
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _metricLine(
    String title,
    String value,
    IconData icon,
  ) {
    return Padding(
      padding:
          const EdgeInsets.only(bottom: 10),
      child: Row(
        children: [
          Icon(
            icon,
            size: 18,
            color: Colors.lightBlueAccent,
          ),
          const SizedBox(width: 9),
          Expanded(
            child: Text(
              title,
              style: const TextStyle(
                color: Colors.white60,
                fontSize: 12,
              ),
            ),
          ),
          Text(
            value,
            style: const TextStyle(
              fontWeight: FontWeight.w800,
            ),
          ),
        ],
      ),
    );
  }

  Widget _dataChip(
    String label,
    String value, {
    Color color = Colors.white,
  }) {
    return Container(
      padding:
          const EdgeInsets.symmetric(
        horizontal: 11,
        vertical: 8,
      ),
      decoration: BoxDecoration(
        color: color.withAlpha(17),
        borderRadius:
            BorderRadius.circular(12),
        border: Border.all(
          color: color.withAlpha(35),
        ),
      ),
      child: Text(
        '$label: $value',
        style: TextStyle(
          fontSize: 11,
          color: color,
          fontWeight: FontWeight.w700,
        ),
      ),
    );
  }

  Widget _buildAiRecommendation() {
    final recommendation =
        _recommendedExit;

    if (recommendation == null) {
      return _glassCard(
        child: const Text(
          'Waiting for AI recommendation...',
          style: TextStyle(
            color: Colors.white60,
          ),
        ),
      );
    }

    final name =
        recommendation['name']
                ?.toString() ??
            '--';

    final queue =
        _toInt(
      recommendation['queue_length'],
    );

    final waiting =
        _toDouble(
      recommendation['waiting_time'],
    );

    final distance =
        _toDouble(
      recommendation['distance'],
    );

    final congestion =
        recommendation['congestion_level']
                ?.toString() ??
            'UNKNOWN';

    final score =
        _toDouble(
      recommendation['score'],
    );

    final trafficColor =
        _congestionColor(
      congestion,
    );

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient:
            const LinearGradient(
          colors: [
            Color(0xFF163E70),
            Color(0xFF172949),
          ],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius:
            BorderRadius.circular(24),
        border: Border.all(
          color:
              Colors.lightBlueAccent
                  .withAlpha(90),
        ),
      ),
      child: Column(
        crossAxisAlignment:
            CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                width: 38,
                height: 38,
                decoration:
                    BoxDecoration(
                  color:
                      Colors.amberAccent
                          .withAlpha(25),
                  shape: BoxShape.circle,
                ),
                child:
                    const Icon(
                  Icons.auto_awesome,
                  color:
                      Colors.amberAccent,
                ),
              ),
              const SizedBox(width: 10),
              const Expanded(
                child: Column(
                  crossAxisAlignment:
                      CrossAxisAlignment.start,
                  children: [
                    Text(
                      'AI EXIT DECISION',
                      style: TextStyle(
                        fontWeight:
                            FontWeight.w900,
                        letterSpacing:
                            1.1,
                      ),
                    ),
                    Text(
                      'Updated from live parking data',
                      style: TextStyle(
                        fontSize: 11,
                        color:
                            Colors.white60,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 17),
          Text(
            name,
            style:
                const TextStyle(
              fontSize: 34,
              fontWeight:
                  FontWeight.w900,
            ),
          ),
          const SizedBox(height: 14),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: [
              _dataChip(
                'Queue',
                '$queue',
              ),
              _dataChip(
                'Wait',
                '${waiting.toStringAsFixed(1)} min',
              ),
              _dataChip(
                'Distance',
                '${distance.toStringAsFixed(0)} m',
              ),
              _dataChip(
                'Traffic',
                congestion,
                color: trafficColor,
              ),
              _dataChip(
                'AI Score',
                score.toStringAsFixed(2),
              ),
            ],
          ),
          if (_alternativeExits.isNotEmpty) ...[
            const SizedBox(height: 18),
            const Text(
              'ALTERNATIVE EXITS',
              style: TextStyle(
                fontSize: 11,
                fontWeight:
                    FontWeight.w900,
                letterSpacing: 1,
                color: Colors.white60,
              ),
            ),
            const SizedBox(height: 8),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children:
                  _alternativeExits.map(
                (exit) {
                  if (exit is! Map) {
                    return const SizedBox.shrink();
                  }

                  final data =
                      Map<String, dynamic>
                          .from(exit);

                  final exitName =
                      data['name']
                              ?.toString() ??
                          'Exit';

                  final exitScore =
                      _toDouble(
                    data['score'],
                  );

                  final exitQueue =
                      _toInt(
                    data['queue_length'],
                  );

                  return Container(
                    padding:
                        const EdgeInsets.symmetric(
                      horizontal: 11,
                      vertical: 8,
                    ),
                    decoration:
                        BoxDecoration(
                      color:
                          Colors.white
                              .withAlpha(12),
                      borderRadius:
                          BorderRadius.circular(
                        12,
                      ),
                      border: Border.all(
                        color:
                            Colors.white
                                .withAlpha(25),
                      ),
                    ),
                    child: Text(
                      '$exitName • Q $exitQueue • ${exitScore.toStringAsFixed(2)}',
                      style:
                          const TextStyle(
                        fontSize: 11,
                        color:
                            Colors.white70,
                      ),
                    ),
                  );
                },
              ).toList(),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildMiniParkingMap() {
    final spaces =
        _parkingSpaces.isEmpty
            ? {
                'P001': false,
                'P002': false,
                'P003': false,
                'P004': false,
                'P005': false,
                'P006': false,
                'P007': false,
              }
            : _parkingSpaces;

    return _glassCard(
      child: Column(
        crossAxisAlignment:
            CrossAxisAlignment.start,
        children: [
          const Text(
            'LIVE PARKING MAP',
            style: TextStyle(
              fontWeight:
                  FontWeight.w900,
              letterSpacing: 1,
            ),
          ),
          const SizedBox(height: 6),
          const Text(
            'Green = available  •  Red = occupied',
            style: TextStyle(
              fontSize: 11,
              color: Colors.white54,
            ),
          ),
          const SizedBox(height: 14),
          GridView.builder(
            shrinkWrap: true,
            physics:
                const NeverScrollableScrollPhysics(),
            itemCount: spaces.length,
            gridDelegate:
                const SliverGridDelegateWithFixedCrossAxisCount(
              crossAxisCount: 2,
              crossAxisSpacing: 9,
              mainAxisSpacing: 9,
              childAspectRatio: 1.7,
            ),
            itemBuilder: (context, index) {
              final entry =
                  spaces.entries.elementAt(index);

              return _parkingSpaceTile(
                entry.key,
                entry.value,
              );
            },
          ),
        ],
      ),
    );
  }

  Widget _parkingSpaceTile(
    String name,
    bool occupied,
  ) {
    final color =
        occupied
            ? Colors.redAccent
            : Colors.greenAccent;

    return Container(
      decoration:
          BoxDecoration(
        color: color.withAlpha(15),
        borderRadius:
            BorderRadius.circular(16),
        border: Border.all(
          color: color.withAlpha(80),
        ),
      ),
      child: Row(
        children: [
          const SizedBox(width: 10),
          Icon(
            occupied
                ? Icons.directions_car_filled
                : Icons.local_parking_rounded,
            color: color,
            size: 25,
          ),
          const SizedBox(width: 9),
          Column(
            mainAxisAlignment:
                MainAxisAlignment.center,
            crossAxisAlignment:
                CrossAxisAlignment.start,
            children: [
              Text(
                name,
                style:
                    const TextStyle(
                  fontWeight:
                      FontWeight.w800,
                ),
              ),
              Text(
                occupied
                    ? 'OCCUPIED'
                    : 'FREE',
                style: TextStyle(
                  color: color,
                  fontSize: 10,
                  fontWeight:
                      FontWeight.w700,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildTrafficPulse() {
    return _glassCard(
      child: Column(
        crossAxisAlignment:
            CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(
                Icons.traffic_rounded,
                color: Colors.orangeAccent,
              ),
              const SizedBox(width: 9),
              const Expanded(
                child: Text(
                  'EXIT TRAFFIC PULSE',
                  style: TextStyle(
                    fontWeight:
                        FontWeight.w900,
                    letterSpacing: 1,
                  ),
                ),
              ),
              Text(
                '${_exits.length} exits',
                style: const TextStyle(
                  color: Colors.white54,
                  fontSize: 11,
                ),
              ),
            ],
          ),
          const SizedBox(height: 15),
          ..._exits.map(
            (exit) {
              if (exit is! Map) {
                return const SizedBox.shrink();
              }

              final map =
                  Map<String, dynamic>.from(
                exit,
              );

              final name =
                  map['name']
                          ?.toString() ??
                      'Exit';

              final queue =
                  _toInt(
                map['queue_length'],
              );

              final congestion =
                  map['congestion_level']
                          ?.toString() ??
                      'LOW';

              final color =
                  _congestionColor(
                congestion,
              );

              final width =
                  (queue / 50)
                      .clamp(
                        0.05,
                        1.0,
                      );

              return Padding(
                padding:
                    const EdgeInsets.only(
                  bottom: 13,
                ),
                child: Column(
                  crossAxisAlignment:
                      CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Expanded(
                          child: Text(
                            name,
                            style:
                                const TextStyle(
                              fontWeight:
                                  FontWeight.w700,
                            ),
                          ),
                        ),
                        Text(
                          'Q $queue',
                          style:
                              TextStyle(
                            color: color,
                            fontSize: 11,
                            fontWeight:
                                FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 7),
                    ClipRRect(
                      borderRadius:
                          BorderRadius.circular(8),
                      child:
                          LinearProgressIndicator(
                        value: width,
                        minHeight: 8,
                        color: color,
                        backgroundColor:
                            Colors.white10,
                      ),
                    ),
                  ],
                ),
              );
            },
          ),
        ],
      ),
    );
  }

  Widget _buildVehicleSummary() {
    return _glassCard(
      child: Row(
        children: [
          Container(
            width: 48,
            height: 48,
            decoration: BoxDecoration(
              color: Colors.cyanAccent
                  .withAlpha(18),
              borderRadius:
                  BorderRadius.circular(15),
            ),
            child: const Icon(
              Icons.directions_car_rounded,
              color: Colors.cyanAccent,
            ),
          ),
          const SizedBox(width: 13),
          Expanded(
            child: Column(
              crossAxisAlignment:
                  CrossAxisAlignment.start,
              children: [
                const Text(
                  'ACTIVE VEHICLES',
                  style: TextStyle(
                    fontSize: 11,
                    color: Colors.white54,
                    fontWeight:
                        FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 3),
                Text(
                  '$_activeVehicles',
                  style:
                      const TextStyle(
                    fontSize: 25,
                    fontWeight:
                        FontWeight.w900,
                  ),
                ),
              ],
            ),
          ),
          _miniCounter(
            'Entries',
            _totalEntries,
          ),
          const SizedBox(width: 12),
          _miniCounter(
            'Exits',
            _totalExits,
          ),
        ],
      ),
    );
  }

  Widget _miniCounter(
    String title,
    int value,
  ) {
    return Column(
      children: [
        Text(
          '$value',
          style:
              const TextStyle(
            fontSize: 20,
            fontWeight:
                FontWeight.w800,
          ),
        ),
        Text(
          title,
          style:
              const TextStyle(
            fontSize: 10,
            color: Colors.white54,
          ),
        ),
      ],
    );
  }

  Widget _buildQuickActionCard() {
    return _glassCard(
      child: Column(
        crossAxisAlignment:
            CrossAxisAlignment.start,
        children: [
          const Text(
            'QUICK ACTIONS',
            style: TextStyle(
              fontWeight:
                  FontWeight.w900,
              letterSpacing: 1,
            ),
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              Expanded(
                child: _quickAction(
                  icon:
                      Icons.local_parking_rounded,
                  title: 'Parking',
                  onTap: () {
                    setState(() {
                      _selectedTab = 1;
                    });
                  },
                ),
              ),
              const SizedBox(width: 9),
              Expanded(
                child: _quickAction(
                  icon: Icons.route_rounded,
                  title: 'Route',
                  onTap: () {
                    setState(() {
                      _selectedTab = 2;
                    });
                  },
                ),
              ),
              const SizedBox(width: 9),
              Expanded(
                child: _quickAction(
                  icon:
                      Icons.warning_amber_rounded,
                  title: 'Alerts',
                  onTap: () {
                    setState(() {
                      _selectedTab = 3;
                    });
                  },
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _quickAction({
    required IconData icon,
    required String title,
    required VoidCallback onTap,
  }) {
    return InkWell(
      onTap: onTap,
      borderRadius:
          BorderRadius.circular(16),
      child: Container(
        padding:
            const EdgeInsets.symmetric(
          vertical: 15,
          horizontal: 9,
        ),
        decoration: BoxDecoration(
          color: Colors.white.withAlpha(10),
          borderRadius:
              BorderRadius.circular(16),
        ),
        child: Column(
          children: [
            Icon(
              icon,
              color:
                  Colors.lightBlueAccent,
            ),
            const SizedBox(height: 7),
            Text(
              title,
              style:
                  const TextStyle(
                fontSize: 11,
                fontWeight:
                    FontWeight.w700,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildDashboard() {
    return RefreshIndicator(
      color: Colors.cyanAccent,
      backgroundColor:
          const Color(0xFF101D31),
      onRefresh: _loadDashboard,
      child: ListView(
        padding:
            const EdgeInsets.fromLTRB(
          16,
          12,
          16,
          28,
        ),
        children: [
          _buildHeader(),
          const SizedBox(height: 14),
          _buildLiveStatusRow(),
          const SizedBox(height: 16),
          _buildOccupancyHero(),
          const SizedBox(height: 16),
          _buildAiRecommendation(),
          const SizedBox(height: 16),
          _buildMiniParkingMap(),
          const SizedBox(height: 16),
          _buildTrafficPulse(),
          const SizedBox(height: 16),
          _buildVehicleSummary(),
          const SizedBox(height: 16),
          _buildQuickActionCard(),
        ],
      ),
    );
  }

  Widget _buildParkingPage() {
    final spaces =
        _parkingSpaces.isEmpty
            ? {
                'P001': false,
                'P002': false,
                'P003': false,
                'P004': false,
                'P005': false,
                'P006': false,
                'P007': false,
              }
            : _parkingSpaces;

    return RefreshIndicator(
      color: Colors.cyanAccent,
      backgroundColor:
          const Color(0xFF101D31),
      onRefresh: _loadDashboard,
      child: ListView(
        padding:
            const EdgeInsets.all(16),
        children: [
          _pageTitle(
            'Parking Center',
            'Live space availability',
            Icons.local_parking_rounded,
          ),
          const SizedBox(height: 16),
          _glassCard(
            child: Column(
              crossAxisAlignment:
                  CrossAxisAlignment.start,
              children: [
                const Text(
                  'SPACE UTILIZATION',
                  style: TextStyle(
                    fontWeight:
                        FontWeight.w900,
                    letterSpacing: 1,
                  ),
                ),
                const SizedBox(height: 14),
                Row(
                  children: [
                    Expanded(
                      child: _bigNumber(
                        '$_totalSpaces',
                        'Total',
                        Colors.white,
                      ),
                    ),
                    Expanded(
                      child: _bigNumber(
                        '$_occupiedSpaces',
                        'Occupied',
                        Colors.redAccent,
                      ),
                    ),
                    Expanded(
                      child: _bigNumber(
                        '$_availableSpaces',
                        'Available',
                        Colors.greenAccent,
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),
          _glassCard(
            child: Column(
              crossAxisAlignment:
                  CrossAxisAlignment.start,
              children: [
                const Text(
                  'PARKING GRID',
                  style: TextStyle(
                    fontWeight:
                        FontWeight.w900,
                    letterSpacing: 1,
                  ),
                ),
                const SizedBox(height: 12),
                GridView.builder(
                  shrinkWrap: true,
                  physics:
                      const NeverScrollableScrollPhysics(),
                  itemCount: spaces.length,
                  gridDelegate:
                      const SliverGridDelegateWithFixedCrossAxisCount(
                    crossAxisCount: 2,
                    crossAxisSpacing: 10,
                    mainAxisSpacing: 10,
                    childAspectRatio: 1.25,
                  ),
                  itemBuilder:
                      (context, index) {
                    final entry =
                        spaces.entries
                            .elementAt(index);

                    return _largeParkingTile(
                      entry.key,
                      entry.value,
                    );
                  },
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _largeParkingTile(
    String name,
    bool occupied,
  ) {
    final color =
        occupied
            ? Colors.redAccent
            : Colors.greenAccent;

    return Container(
      decoration:
          BoxDecoration(
        gradient:
            LinearGradient(
          colors: [
            color.withAlpha(22),
            const Color(0xFF111F33),
          ],
        ),
        borderRadius:
            BorderRadius.circular(20),
        border: Border.all(
          color: color.withAlpha(85),
        ),
      ),
      child: Column(
        mainAxisAlignment:
            MainAxisAlignment.center,
        children: [
          Icon(
            occupied
                ? Icons.directions_car_filled_rounded
                : Icons.local_parking_rounded,
            size: 38,
            color: color,
          ),
          const SizedBox(height: 10),
          Text(
            name,
            style:
                const TextStyle(
              fontWeight: FontWeight.w900,
              fontSize: 17,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            occupied
                ? 'OCCUPIED'
                : 'AVAILABLE',
            style: TextStyle(
              color: color,
              fontWeight:
                  FontWeight.bold,
              fontSize: 11,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildRoutePage() {
    return ListView(
      padding:
          const EdgeInsets.all(16),
      children: [
        _pageTitle(
          'Smart Route',
          'AI-powered exit guidance',
          Icons.route_rounded,
        ),
        const SizedBox(height: 16),
        _glassCard(
          child: Column(
            crossAxisAlignment:
                CrossAxisAlignment.start,
            children: [
              const Text(
                'VEHICLE IDENTIFICATION',
                style: TextStyle(
                  fontWeight:
                      FontWeight.w900,
                  letterSpacing: 1,
                ),
              ),
              const SizedBox(height: 12),
              TextField(
                controller:
                    _vehicleController,
                textCapitalization:
                    TextCapitalization.characters,
                decoration:
                    InputDecoration(
                  filled: true,
                  fillColor:
                      Colors.black12,
                  labelText:
                      'Vehicle Number',
                  hintText:
                      'TN03EF9012',
                  prefixIcon:
                      const Icon(
                    Icons.directions_car_rounded,
                  ),
                  border:
                      OutlineInputBorder(
                    borderRadius:
                        BorderRadius.circular(
                      16,
                    ),
                  ),
                ),
              ),
              const SizedBox(height: 12),
              SizedBox(
                width: double.infinity,
                child:
                    FilledButton.icon(
                  onPressed:
                      _routeLoading
                          ? null
                          : _loadVehicleRoute,
                  icon: _routeLoading
                      ? const SizedBox(
                          width: 18,
                          height: 18,
                          child:
                              CircularProgressIndicator(
                            strokeWidth: 2,
                          ),
                        )
                      : const Icon(
                          Icons.auto_awesome,
                        ),
                  label: Text(
                    _routeLoading
                        ? 'Calculating...'
                        : 'Get AI Route',
                  ),
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 16),
        if (_vehicleRoute != null)
          _buildVehicleRouteCard()
        else
          _glassCard(
            child: const Column(
              children: [
                Icon(
                  Icons.route_outlined,
                  size: 45,
                  color: Colors.white38,
                ),
                SizedBox(height: 10),
                Text(
                  'Enter your vehicle number and request an AI route.',
                  textAlign:
                      TextAlign.center,
                  style: TextStyle(
                    color: Colors.white54,
                  ),
                ),
              ],
            ),
          ),
      ],
    );
  }

  Widget _buildVehicleRouteCard() {
    final route = _vehicleRoute!;

    final steps =
        route['route'] is List
            ? (route['route'] as List)
                .map(
                  (item) =>
                      item.toString(),
                )
                .toList()
            : <String>[];

    final exit =
        route['recommended_exit']
                ?.toString() ??
            '--';

    final distance =
        _toDouble(
      route['distance'],
    );

    final waiting =
        _toDouble(
      route['estimated_waiting_time'],
    );

    final congestion =
        route['congestion']
                ?.toString() ??
            'UNKNOWN';

    final color =
        _congestionColor(
      congestion,
    );

    return _glassCard(
      child: Column(
        crossAxisAlignment:
            CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(
                Icons.navigation_rounded,
                color: Colors.cyanAccent,
              ),
              const SizedBox(width: 9),
              const Text(
                'AI ROUTE RESULT',
                style: TextStyle(
                  fontWeight:
                      FontWeight.w900,
                  letterSpacing: 1,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Text(
            exit,
            style:
                const TextStyle(
              fontSize: 32,
              fontWeight:
                  FontWeight.w900,
              color: Colors.cyanAccent,
            ),
          ),
          const Text(
            'Recommended Exit',
            style: TextStyle(
              color: Colors.white54,
              fontSize: 11,
            ),
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              Expanded(
                child: _routeMetric(
                  'Distance',
                  '${distance.toStringAsFixed(0)} m',
                  Icons.straighten_rounded,
                ),
              ),
              Expanded(
                child: _routeMetric(
                  'Waiting',
                  '${waiting.toStringAsFixed(1)} min',
                  Icons.timer_outlined,
                ),
              ),
              Expanded(
                child: _routeMetric(
                  'Traffic',
                  congestion,
                  Icons.traffic_rounded,
                  color: color,
                ),
              ),
            ],
          ),
          const SizedBox(height: 18),
          const Text(
            'ROUTE TIMELINE',
            style: TextStyle(
              fontWeight:
                  FontWeight.w900,
              letterSpacing: 1,
            ),
          ),
          const SizedBox(height: 14),
          for (int i = 0;
              i < steps.length;
              i++)
            _routeStep(
              index: i,
              text: steps[i],
              isLast:
                  i == steps.length - 1,
            ),
        ],
      ),
    );
  }

  Widget _routeMetric(
    String title,
    String value,
    IconData icon, {
    Color color = Colors.white,
  }) {
    return Column(
      children: [
        Icon(
          icon,
          color: color,
          size: 22,
        ),
        const SizedBox(height: 6),
        Text(
          value,
          style:
              const TextStyle(
            fontWeight:
                FontWeight.w900,
            fontSize: 13,
          ),
          textAlign:
              TextAlign.center,
        ),
        Text(
          title,
          style:
              const TextStyle(
            color: Colors.white54,
            fontSize: 10,
          ),
        ),
      ],
    );
  }

  Widget _routeStep({
    required int index,
    required String text,
    required bool isLast,
  }) {
    return Row(
      crossAxisAlignment:
          CrossAxisAlignment.start,
      children: [
        Column(
          children: [
            Container(
              width: 30,
              height: 30,
              decoration:
                  const BoxDecoration(
                shape: BoxShape.circle,
                color: Colors.blueAccent,
              ),
              alignment:
                  Alignment.center,
              child: Text(
                '${index + 1}',
                style:
                    const TextStyle(
                  fontWeight:
                      FontWeight.bold,
                ),
              ),
            ),
            if (!isLast)
              Container(
                width: 2,
                height: 34,
                color: Colors.blueAccent
                    .withAlpha(100),
              ),
          ],
        ),
        const SizedBox(width: 12),
        Padding(
          padding:
              const EdgeInsets.only(
            top: 5,
          ),
          child: Text(
            text,
            style:
                const TextStyle(
              fontSize: 14,
              fontWeight:
                  FontWeight.w600,
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildAlertsPage() {
    return RefreshIndicator(
      color: Colors.cyanAccent,
      backgroundColor:
          const Color(0xFF101D31),
      onRefresh: _loadDashboard,
      child: ListView(
        padding:
            const EdgeInsets.all(16),
        children: [
          _pageTitle(
            'Alerts Center',
            'Parking and exit conditions',
            Icons.warning_amber_rounded,
          ),
          const SizedBox(height: 16),
          _glassCard(
            child: Column(
              crossAxisAlignment:
                  CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Container(
                      width: 42,
                      height: 42,
                      decoration:
                          BoxDecoration(
                        color: Colors.orangeAccent
                            .withAlpha(18),
                        shape:
                            BoxShape.circle,
                      ),
                      child:
                          const Icon(
                        Icons.notifications_active_rounded,
                        color:
                            Colors.orangeAccent,
                      ),
                    ),
                    const SizedBox(width: 10),
                    const Text(
                      'LIVE ALERTS',
                      style: TextStyle(
                        fontWeight:
                            FontWeight.w900,
                        letterSpacing: 1,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 15),
                ..._alerts.map(
                  (alert) {
                    final emergency =
                        alert.contains(
                      '🚨',
                    );

                    return Container(
                      width: double.infinity,
                      margin:
                          const EdgeInsets.only(
                        bottom: 10,
                      ),
                      padding:
                          const EdgeInsets.all(
                        13,
                      ),
                      decoration:
                          BoxDecoration(
                        color: emergency
                            ? Colors.redAccent
                                .withAlpha(20)
                            : Colors.white
                                .withAlpha(8),
                        borderRadius:
                            BorderRadius.circular(
                          14,
                        ),
                      ),
                      child: Text(
                        alert,
                        style: TextStyle(
                          color: emergency
                              ? Colors.redAccent
                              : Colors.white70,
                          fontWeight:
                              FontWeight.w600,
                        ),
                      ),
                    );
                  },
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),
          _glassCard(
            child: Column(
              crossAxisAlignment:
                  CrossAxisAlignment.start,
              children: [
                const Text(
                  'EXIT STATUS',
                  style: TextStyle(
                    fontWeight:
                        FontWeight.w900,
                    letterSpacing: 1,
                  ),
                ),
                const SizedBox(height: 13),
                ..._exits.map(
                  (exit) {
                    if (exit is! Map) {
                      return const SizedBox.shrink();
                    }

                    final map =
                        Map<String, dynamic>.from(
                      exit,
                    );

                    final name =
                        map['name']
                                ?.toString() ??
                            'Exit';

                    final available =
                        map['is_available'] == true;

                    final congestion =
                        map['congestion_level']
                                ?.toString() ??
                            'LOW';

                    final color =
                        available
                            ? _availabilityColor(
                                available,
                              )
                            : Colors.redAccent;

                    return Container(
                      margin:
                          const EdgeInsets.only(
                        bottom: 10,
                      ),
                      padding:
                          const EdgeInsets.all(
                        14,
                      ),
                      decoration:
                          BoxDecoration(
                        color: Colors.white
                            .withAlpha(7),
                        borderRadius:
                            BorderRadius.circular(
                          15,
                        ),
                      ),
                      child: Row(
                        children: [
                          Container(
                            width: 10,
                            height: 10,
                            decoration:
                                BoxDecoration(
                              shape:
                                  BoxShape.circle,
                              color: color,
                            ),
                          ),
                          const SizedBox(width: 10),
                          Expanded(
                            child: Column(
                              crossAxisAlignment:
                                  CrossAxisAlignment.start,
                              children: [
                                Text(
                                  name,
                                  style:
                                      const TextStyle(
                                    fontWeight:
                                        FontWeight.w800,
                                  ),
                                ),
                                Text(
                                  available
                                      ? congestion
                                      : 'BLOCKED',
                                  style:
                                      TextStyle(
                                    color:
                                        available
                                            ? _congestionColor(
                                                congestion,
                                              )
                                            : Colors.redAccent,
                                    fontSize:
                                        10,
                                  ),
                                ),
                              ],
                            ),
                          ),
                          Text(
                            'Q ${_toInt(map['queue_length'])}',
                            style:
                                const TextStyle(
                              color:
                                  Colors.white60,
                              fontSize: 11,
                            ),
                          ),
                        ],
                      ),
                    );
                  },
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _pageTitle(
    String title,
    String subtitle,
    IconData icon,
  ) {
    return Row(
      children: [
        Container(
          width: 48,
          height: 48,
          decoration:
              BoxDecoration(
            color:
                Colors.blueAccent
                    .withAlpha(25),
            borderRadius:
                BorderRadius.circular(15),
          ),
          child: Icon(
            icon,
            color:
                Colors.lightBlueAccent,
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: Column(
            crossAxisAlignment:
                CrossAxisAlignment.start,
            children: [
              Text(
                title,
                style:
                    const TextStyle(
                  fontSize: 23,
                  fontWeight:
                      FontWeight.w900,
                ),
              ),
              Text(
                subtitle,
                style:
                    const TextStyle(
                  color: Colors.white54,
                  fontSize: 11,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _bigNumber(
    String value,
    String label,
    Color color,
  ) {
    return Column(
      children: [
        Text(
          value,
          style:
              TextStyle(
            fontSize: 28,
            fontWeight:
                FontWeight.w900,
            color: color,
          ),
        ),
        const SizedBox(height: 3),
        Text(
          label,
          style:
              const TextStyle(
            fontSize: 10,
            color: Colors.white54,
          ),
        ),
      ],
    );
  }

  Widget _buildBody() {
    switch (_selectedTab) {
      case 1:
        return _buildParkingPage();

      case 2:
        return _buildRoutePage();

      case 3:
        return _buildAlertsPage();

      default:
        return _buildDashboard();
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: _loading && !_backendOnline
            ? const Center(
                child:
                    CircularProgressIndicator(
                  color: Colors.cyanAccent,
                ),
              )
            : _buildBody(),
      ),
      bottomNavigationBar:
          NavigationBar(
        selectedIndex:
            _selectedTab,
        onDestinationSelected:
            (index) {
          setState(() {
            _selectedTab = index;
          });
        },
        backgroundColor:
            const Color(0xFF0A1626),
        indicatorColor:
            Colors.blueAccent
                .withAlpha(45),
        destinations: const [
          NavigationDestination(
            icon: Icon(
              Icons.dashboard_outlined,
            ),
            selectedIcon: Icon(
              Icons.dashboard_rounded,
            ),
            label: 'Dashboard',
          ),
          NavigationDestination(
            icon: Icon(
              Icons.local_parking_outlined,
            ),
            selectedIcon: Icon(
              Icons.local_parking_rounded,
            ),
            label: 'Parking',
          ),
          NavigationDestination(
            icon: Icon(
              Icons.route_outlined,
            ),
            selectedIcon: Icon(
              Icons.route_rounded,
            ),
            label: 'Route',
          ),
          NavigationDestination(
            icon: Icon(
              Icons.notifications_none_rounded,
            ),
            selectedIcon: Icon(
              Icons.notifications_rounded,
            ),
            label: 'Alerts',
          ),
        ],
      ),
    );
  }
}