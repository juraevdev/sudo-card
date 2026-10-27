import 'dart:ui';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:sudo_e_card/data/student_card.dart';
import 'package:sudo_e_card/screens/card_screen.dart';
import 'package:sudo_e_card/widgets/flip_card.dart';

StudentCard _sampleCard() => StudentCard(
      fullName: 'Murodov Behruz',
      studentId: 'SA-104237',
      cardId: 'UZN-2026-0142',
      organization: 'JizPi IT PARK',
      access: 'STUDENT',
      issueDate: DateTime(2026, 10, 5),
      validUntil: DateTime(2027, 10, 5),
      qrPayload: 'UZN.test-opaque-token',
    );

void main() {
  test('QR payload is opaque (no PII JSON)', () {
    final card = _sampleCard();
    expect(card.qrPayload.startsWith('UZN.'), isTrue);
    expect(card.qrPayload.contains(card.fullName), isFalse);
    expect(card.qrPayload.contains('{'), isFalse);
  });

  testWidgets('Card flips to the back on swipe', (tester) async {
    await tester.pumpWidget(MaterialApp(home: CardScreen(card: _sampleCard())));
    expect(find.text('FRONT'), findsOneWidget);
    expect(find.text('Murodov Behruz'), findsOneWidget);

    await tester.fling(find.text('STUDENT ACCESS'), const Offset(300, 0), 1500);
    await tester.pumpAndSettle();

    expect(find.text('BACK'), findsOneWidget);
    expect(find.text('UZN-2026-0142'), findsOneWidget);
  });

  testWidgets('Left fling also shows the back face', (tester) async {
    await tester.pumpWidget(MaterialApp(home: CardScreen(card: _sampleCard())));

    await tester.fling(find.text('STUDENT ACCESS'), const Offset(-300, 0), 1500);
    await tester.pumpAndSettle();

    expect(find.text('BACK'), findsOneWidget);
  });

  testWidgets('Card is vertical on a phone-sized screen', (tester) async {
    tester.view.physicalSize = const Size(1080, 2340);
    tester.view.devicePixelRatio = 2.625;
    addTearDown(tester.view.reset);

    await tester.pumpWidget(MaterialApp(home: CardScreen(card: _sampleCard())));
    final card = tester.getSize(find.byType(FlipCard));
    expect(card.height, greaterThan(card.width));
  });
}
