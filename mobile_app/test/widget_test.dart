import 'package:flutter_test/flutter_test.dart';
import 'package:mobile_app/main.dart';

void main() {
  testWidgets(
    'AI Parking Exit Optimizer loads',
    (WidgetTester tester) async {
      await tester.pumpWidget(
        const ParkingApp(),
      );

      expect(
        find.text('AI Parking Exit'),
        findsOneWidget,
      );

      expect(
        find.text('Parking Overview'),
        findsOneWidget,
      );

      expect(
        find.text('Parking Spaces'),
        findsOneWidget,
      );
    },
  );
}