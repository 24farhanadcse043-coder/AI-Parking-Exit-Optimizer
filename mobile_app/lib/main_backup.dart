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
      title: 'AI Parking Exit Optimizer',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        useMaterial3: true,
        colorScheme: ColorScheme.fromSeed(
          seedColor: Colors.blue,
          brightness: Brightness.dark,
        ),
        scaffoldBackgroundColor: const Color(0xFF0B1220),
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
static const String baseUrl = 'http://192.168.1.4:8000';
static const String websocketUrl =
    'ws://192.168.1.4:8000/ws/recommendations';

  Timer? _refreshTimer;
  WebSocketChannel? _recommendationChannel;

  bool _loading = true;
  bool _backendOnline = false;
  bool _cameraOnline = false;

  String? _errorMessage;

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

  Map<String, dynamic>? _vehicleRoute;

  final TextEditingController _vehicleController =
      TextEditingController(
    text: 'TN03EF9012',
  );

  @override
  void initState() {
    super.initState();

    _loadDashboard();

    _refreshTimer = Timer.periodic(
      const Duration(seconds: 5),
      (_) => _loadDashboard(),
    );

    _connectRecommendationWebSocket();
  }

  @override
  void dispose() {
    _refreshTimer?.cancel();
    _recommendationChannel?.sink.close();
    _vehicleController.dispose();
    super.dispose();
  }

  Future<Map<String, dynamic>> _getJson(
    String endpoint,
  ) async {
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

    return jsonDecode(response.body)
        as Map<String, dynamic>;
  }

  Future<void> _loadDashboard() async {
    try {
      final visionStatus =
          await _getJson('/api/vision/status');

      final cameraStatus =
          await _getJson(
        '/api/vision/camera/status',
      );

      final recommendation =
          await _getJson(
        '/api/recommendations/',
      );

      if (!mounted) return;

      final parkingVision =
          visionStatus['parking_vision']
              as Map<String, dynamic>?;

      final occupancy =
          parkingVision?['occupancy']
              as Map<String, dynamic>?;

      final tracking =
          parkingVision?['vehicle_tracking']
              as Map<String, dynamic>?;

      final recommendationData =
          recommendation['recommended_exit']
              as Map<String, dynamic>?;

      final alternatives =
          recommendation['alternatives']
              as List<dynamic>?;

      setState(() {
        _backendOnline = true;

        _cameraOnline =
            cameraStatus['camera'] == 'ONLINE';

        _loading = false;
        _errorMessage = null;

        _totalSpaces =
            (occupancy?['total_spaces'] ?? 0)
                as int;

        _occupiedSpaces =
            (occupancy?['occupied_spaces'] ?? 0)
                as int;

        _availableSpaces =
            (occupancy?['available_spaces'] ?? 0)
                as int;

        _occupancyPercentage =
            ((occupancy?['occupancy_percentage'] ?? 0)
                    as num)
                .toDouble();

        final rawSpaces =
            occupancy?['spaces']
                as Map<String, dynamic>?;

        _parkingSpaces = rawSpaces?.map(
              (key, value) => MapEntry(
                key,
                value == true,
              ),
            ) ??
            {};

        _activeVehicles =
            (tracking?['active_vehicles'] ?? 0)
                as int;

        _totalEntries =
            (tracking?['total_entries'] ?? 0)
                as int;

        _totalExits =
            (tracking?['total_exits'] ?? 0)
                as int;

        _recommendedExit =
            recommendationData;

        _alternativeExits =
            alternatives ?? [];
      });
    } catch (error) {
      if (!mounted) return;

      setState(() {
        _loading = false;
        _backendOnline = false;
        _errorMessage =
            'Unable to connect to parking server.';
      });
    }
  }

  void _connectRecommendationWebSocket() {
    try {
      _recommendationChannel =
          WebSocketChannel.connect(
        Uri.parse(websocketUrl),
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
            });
          } catch (_) {
            // Ignore malformed WebSocket messages.
          }
        },
        onError: (_) {
          // REST refresh continues to keep the dashboard alive.
        },
        onDone: () {
          // REST polling remains active.
        },
      );
    } catch (_) {
      // REST API remains available if WebSocket is unavailable.
    }
  }

  Future<void> _loadVehicleRoute() async {
    final vehicleNumber =
        _vehicleController.text.trim();

    if (vehicleNumber.isEmpty) {
      _showMessage(
        'Enter a vehicle number.',
      );
      return;
    }

    setState(() {
      _vehicleRoute = null;
    });

    try {
      final route =
          await _getJson(
        '/api/routes/$vehicleNumber',
      );

      if (!mounted) return;

      setState(() {
        _vehicleRoute = route;
      });
    } catch (error) {
      if (!mounted) return;

      _showMessage(
        'Unable to calculate route for $vehicleNumber.',
      );
    }
  }

  void _showMessage(String message) {
    ScaffoldMessenger.of(context)
        .showSnackBar(
      SnackBar(
        content: Text(message),
      ),
    );
  }

  Color _statusColor(
    bool active,
  ) {
    return active
        ? Colors.greenAccent
        : Colors.redAccent;
  }

  Widget _buildStatusCard({
    required IconData icon,
    required String title,
    required String value,
    required Color color,
  }) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: const Color(0xFF121C2E),
          borderRadius:
              BorderRadius.circular(18),
          border: Border.all(
            color: color.withAlpha(70),
          ),
        ),
        child: Column(
          crossAxisAlignment:
              CrossAxisAlignment.start,
          children: [
            Icon(
              icon,
              color: color,
              size: 28,
            ),
            const SizedBox(height: 10),
            Text(
              title,
              style: const TextStyle(
                color: Colors.white70,
                fontSize: 12,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              value,
              style: const TextStyle(
                color: Colors.white,
                fontSize: 17,
                fontWeight: FontWeight.bold,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildParkingSpace(
    String spaceNumber,
    bool occupied,
  ) {
    final color = occupied
        ? Colors.redAccent
        : Colors.greenAccent;

    return Container(
      padding: const EdgeInsets.symmetric(
        vertical: 14,
        horizontal: 10,
      ),
      decoration: BoxDecoration(
        color: color.withAlpha(25),
        borderRadius:
            BorderRadius.circular(14),
        border: Border.all(
          color: color.withAlpha(140),
        ),
      ),
      child: Column(
        children: [
          Icon(
            occupied
                ? Icons.directions_car
                : Icons.local_parking,
            color: color,
            size: 28,
          ),
          const SizedBox(height: 6),
          Text(
            spaceNumber,
            style: const TextStyle(
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 2),
          Text(
            occupied ? 'OCCUPIED' : 'FREE',
            style: TextStyle(
              color: color,
              fontSize: 11,
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildRecommendationCard() {
    final recommended =
        _recommendedExit;

    if (recommended == null) {
      return const SizedBox.shrink();
    }

    final name =
        recommended['name'] ?? 'Unknown';

    final congestion =
        recommended['congestion_level'] ??
            'UNKNOWN';

    final queue =
        recommended['queue_length'] ?? 0;

    final waiting =
        ((recommended['waiting_time'] ?? 0)
                as num)
            .toDouble();

    final distance =
        ((recommended['distance'] ?? 0)
                as num)
            .toDouble();

    final score =
        ((recommended['score'] ?? 0)
                as num)
            .toDouble();

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [
            Color(0xFF123B66),
            Color(0xFF142D4C),
          ],
        ),
        borderRadius:
            BorderRadius.circular(22),
        border: Border.all(
          color: Colors.blueAccent.withAlpha(100),
        ),
      ),
      child: Column(
        crossAxisAlignment:
            CrossAxisAlignment.start,
        children: [
          const Row(
            children: [
              Icon(
                Icons.auto_awesome,
                color: Colors.amberAccent,
              ),
              SizedBox(width: 8),
              Text(
                'AI RECOMMENDED EXIT',
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  letterSpacing: 1,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Text(
            name.toString(),
            style: const TextStyle(
              fontSize: 30,
              fontWeight: FontWeight.bold,
              color: Colors.white,
            ),
          ),
          const SizedBox(height: 14),
          Wrap(
            spacing: 10,
            runSpacing: 10,
            children: [
              _infoChip(
                'Queue',
                '$queue',
              ),
              _infoChip(
                'Wait',
                '${waiting.toStringAsFixed(1)} min',
              ),
              _infoChip(
                'Distance',
                '${distance.toStringAsFixed(0)} m',
              ),
              _infoChip(
                'Traffic',
                congestion.toString(),
              ),
              _infoChip(
                'AI Score',
                score.toStringAsFixed(2),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _infoChip(
    String label,
    String value,
  ) {
    return Container(
      padding: const EdgeInsets.symmetric(
        horizontal: 12,
        vertical: 8,
      ),
      decoration: BoxDecoration(
        color: Colors.white.withAlpha(18),
        borderRadius:
            BorderRadius.circular(12),
      ),
      child: Text(
        '$label: $value',
        style: const TextStyle(
          fontSize: 12,
          color: Colors.white,
        ),
      ),
    );
  }

  Widget _buildAlternativeExits() {
    if (_alternativeExits.isEmpty) {
      return const SizedBox.shrink();
    }

    return Column(
      crossAxisAlignment:
          CrossAxisAlignment.start,
      children: [
        const Text(
          'Alternative Exits',
          style: TextStyle(
            fontSize: 19,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 10),
        ..._alternativeExits.map(
          (exit) {
            if (exit is! Map) {
              return const SizedBox.shrink();
            }

            final map =
                Map<String, dynamic>.from(
              exit,
            );

            return Container(
              margin:
                  const EdgeInsets.only(bottom: 10),
              padding:
                  const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color:
                    const Color(0xFF121C2E),
                borderRadius:
                    BorderRadius.circular(16),
              ),
              child: Row(
                children: [
                  const Icon(
                    Icons.alt_route,
                    color: Colors.lightBlueAccent,
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Text(
                      map['name']
                              ?.toString() ??
                          'Exit',
                      style:
                          const TextStyle(
                        fontWeight:
                            FontWeight.bold,
                      ),
                    ),
                  ),
                  Text(
                    '${map['score'] ?? 0}',
                    style: const TextStyle(
                      color:
                          Colors.white70,
                    ),
                  ),
                ],
              ),
            );
          },
        ),
      ],
    );
  }

  Widget _buildRouteCard() {
    if (_vehicleRoute == null) {
      return const SizedBox.shrink();
    }

    final route =
        _vehicleRoute!;

    final routeSteps =
        route['route'] is List
            ? (route['route'] as List)
                .map(
                  (item) =>
                      item.toString(),
                )
                .toList()
            : <String>[];

    return Container(
      width: double.infinity,
      padding:
          const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color:
            const Color(0xFF121C2E),
        borderRadius:
            BorderRadius.circular(20),
        border: Border.all(
          color: Colors.cyanAccent
              .withAlpha(80),
        ),
      ),
      child: Column(
        crossAxisAlignment:
            CrossAxisAlignment.start,
        children: [
          const Row(
            children: [
              Icon(
                Icons.route,
                color:
                    Colors.cyanAccent,
              ),
              SizedBox(width: 8),
              Text(
                'VEHICLE ROUTE',
                style: TextStyle(
                  fontWeight:
                      FontWeight.bold,
                ),
              ),
            ],
          ),
          const SizedBox(height: 14),
          Text(
            route['vehicle_number']
                    ?.toString() ??
                '',
            style: const TextStyle(
              color: Colors.white70,
            ),
          ),
          const SizedBox(height: 10),
          Text(
            route['recommended_exit']
                    ?.toString() ??
                'Unknown',
            style: const TextStyle(
              fontSize: 26,
              fontWeight: FontWeight.bold,
              color:
                  Colors.cyanAccent,
            ),
          ),
          const SizedBox(height: 10),
          Text(
            'Distance: ${route['distance'] ?? 0} m',
          ),
          Text(
            'Waiting: ${route['estimated_waiting_time'] ?? 0} min',
          ),
          Text(
            'Traffic: ${route['congestion'] ?? 'UNKNOWN'}',
          ),
          const SizedBox(height: 14),
          const Text(
            'Route',
            style: TextStyle(
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          for (int i = 0;
              i < routeSteps.length;
              i++)
            Padding(
              padding:
                  const EdgeInsets.only(
                bottom: 6,
              ),
              child: Row(
                children: [
                  CircleAvatar(
                    radius: 11,
                    backgroundColor:
                        Colors.blueAccent,
                    child: Text(
                      '${i + 1}',
                      style:
                          const TextStyle(
                        fontSize: 11,
                        fontWeight:
                            FontWeight.bold,
                      ),
                    ),
                  ),
                  const SizedBox(width: 10),
                  Text(
                    routeSteps[i],
                  ),
                ],
              ),
            ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text(
          'AI Parking Exit',
          style: TextStyle(
            fontWeight: FontWeight.bold,
          ),
        ),
        backgroundColor:
            const Color(0xFF0B1220),
        actions: [
          Padding(
            padding:
                const EdgeInsets.only(
              right: 14,
            ),
            child: Icon(
              Icons.circle,
              size: 12,
              color: _backendOnline
                  ? Colors.greenAccent
                  : Colors.redAccent,
            ),
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: _loadDashboard,
        child: ListView(
          padding:
              const EdgeInsets.all(16),
          children: [
            if (_loading)
              const Padding(
                padding:
                    EdgeInsets.all(30),
                child: Center(
                  child:
                      CircularProgressIndicator(),
                ),
              ),

            if (_errorMessage != null)
              Container(
                margin:
                    const EdgeInsets.only(
                  bottom: 16,
                ),
                padding:
                    const EdgeInsets.all(14),
                decoration: BoxDecoration(
                  color: Colors.redAccent
                      .withAlpha(20),
                  borderRadius:
                      BorderRadius.circular(16),
                  border: Border.all(
                    color: Colors.redAccent
                        .withAlpha(90),
                  ),
                ),
                child: Text(
                  _errorMessage!,
                  style: const TextStyle(
                    color:
                        Colors.redAccent,
                  ),
                ),
              ),

            Row(
              children: [
                _buildStatusCard(
                  icon: Icons.wifi,
                  title: 'Backend',
                  value: _backendOnline
                      ? 'ONLINE'
                      : 'OFFLINE',
                  color: _statusColor(
                    _backendOnline,
                  ),
                ),
                const SizedBox(width: 10),
                _buildStatusCard(
                  icon: Icons.videocam,
                  title: 'Camera',
                  value: _cameraOnline
                      ? 'ONLINE'
                      : 'OFFLINE',
                  color: _statusColor(
                    _cameraOnline,
                  ),
                ),
              ],
            ),

            const SizedBox(height: 16),

            Container(
              padding:
                  const EdgeInsets.all(18),
              decoration: BoxDecoration(
                color:
                    const Color(0xFF121C2E),
                borderRadius:
                    BorderRadius.circular(20),
              ),
              child: Column(
                crossAxisAlignment:
                    CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Parking Overview',
                    style: TextStyle(
                      fontSize: 20,
                      fontWeight:
                          FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 15),
                  Text(
                    '${_occupancyPercentage.toStringAsFixed(2)}% occupied',
                    style: const TextStyle(
                      fontSize: 26,
                      fontWeight:
                          FontWeight.bold,
                      color:
                          Colors.blueAccent,
                    ),
                  ),
                  const SizedBox(height: 8),
                  ClipRRect(
                    borderRadius:
                        BorderRadius.circular(8),
                    child:
                        LinearProgressIndicator(
                      value: (_occupancyPercentage /
                              100)
                          .clamp(0.0, 1.0),
                      minHeight: 10,
                      backgroundColor:
                          Colors.white10,
                    ),
                  ),
                  const SizedBox(height: 15),
                  Row(
                    mainAxisAlignment:
                        MainAxisAlignment
                            .spaceBetween,
                    children: [
                      Text(
                        'Total: $_totalSpaces',
                      ),
                      Text(
                        'Occupied: $_occupiedSpaces',
                      ),
                      Text(
                        'Free: $_availableSpaces',
                      ),
                    ],
                  ),
                ],
              ),
            ),

            const SizedBox(height: 16),

            const Text(
              'Parking Spaces',
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
              ),
            ),

            const SizedBox(height: 10),

            GridView.builder(
              shrinkWrap: true,
              physics:
                  const NeverScrollableScrollPhysics(),
              itemCount:
                  _parkingSpaces.length,
              gridDelegate:
                  const SliverGridDelegateWithFixedCrossAxisCount(
                crossAxisCount: 2,
                crossAxisSpacing: 10,
                mainAxisSpacing: 10,
                childAspectRatio: 1.35,
              ),
              itemBuilder:
                  (context, index) {
                final entry =
                    _parkingSpaces.entries
                        .elementAt(index);

                return _buildParkingSpace(
                  entry.key,
                  entry.value,
                );
              },
            ),

            const SizedBox(height: 20),

            _buildRecommendationCard(),

            const SizedBox(height: 14),

            _buildAlternativeExits(),

            const SizedBox(height: 20),

            Container(
              padding:
                  const EdgeInsets.all(18),
              decoration: BoxDecoration(
                color:
                    const Color(0xFF121C2E),
                borderRadius:
                    BorderRadius.circular(20),
              ),
              child: Column(
                crossAxisAlignment:
                    CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Vehicle Route',
                    style: TextStyle(
                      fontSize: 20,
                      fontWeight:
                          FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 12),
                  TextField(
                    controller:
                        _vehicleController,
                    decoration:
                        InputDecoration(
                      labelText:
                          'Vehicle Number',
                      hintText:
                          'Example: TN03EF9012',
                      prefixIcon:
                          const Icon(
                        Icons.directions_car,
                      ),
                      filled: true,
                      fillColor:
                          Colors.black12,
                      border:
                          OutlineInputBorder(
                        borderRadius:
                            BorderRadius.circular(
                          14,
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(height: 12),
                  SizedBox(
                    width:
                        double.infinity,
                    child:
                        FilledButton.icon(
                      onPressed:
                          _loadVehicleRoute,
                      icon:
                          const Icon(
                        Icons.route,
                      ),
                      label:
                          const Text(
                        'Get AI Route',
                      ),
                    ),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 14),

            _buildRouteCard(),

            const SizedBox(height: 20),

            Container(
              padding:
                  const EdgeInsets.all(18),
              decoration: BoxDecoration(
                color:
                    const Color(0xFF121C2E),
                borderRadius:
                    BorderRadius.circular(20),
              ),
              child: Row(
                mainAxisAlignment:
                    MainAxisAlignment
                        .spaceAround,
                children: [
                  _smallStatistic(
                    'Active',
                    '$_activeVehicles',
                  ),
                  _smallStatistic(
                    'Entries',
                    '$_totalEntries',
                  ),
                  _smallStatistic(
                    'Exits',
                    '$_totalExits',
                  ),
                ],
              ),
            ),

            const SizedBox(height: 20),

            Center(
              child: Text(
                'AI Parking Exit Flow Optimizer',
                style:
                    TextStyle(
                  color:
                      Colors.white54,
                  fontSize: 12,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _smallStatistic(
    String label,
    String value,
  ) {
    return Column(
      children: [
        Text(
          value,
          style: const TextStyle(
            fontSize: 22,
            fontWeight:
                FontWeight.bold,
            color:
                Colors.blueAccent,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          label,
          style: const TextStyle(
            color: Colors.white60,
            fontSize: 12,
          ),
        ),
      ],
    );
  }
}