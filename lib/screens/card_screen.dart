import 'dart:math' as math;

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../data/student_card.dart';
import '../services/session_store.dart';
import '../widgets/card_back.dart';
import '../widgets/card_front.dart';
import '../widgets/card_style.dart';
import '../widgets/flip_card.dart';
import 'login_screen.dart';

class CardScreen extends StatefulWidget {
  const CardScreen({super.key, required this.card, this.store});

  final StudentCard card;
  final SessionStore? store;

  @override
  State<CardScreen> createState() => _CardScreenState();
}

class _CardScreenState extends State<CardScreen> {
  bool _showingBack = false;

  Future<void> _logout() async {
    await (widget.store ?? SessionStore()).clear();
    if (!mounted) return;
    Navigator.of(context).pushReplacement(
      MaterialPageRoute(builder: (_) => const LoginScreen()),
    );
  }

  @override
  Widget build(BuildContext context) {
    final card = widget.card;
    return AnnotatedRegion<SystemUiOverlayStyle>(
      value: SystemUiOverlayStyle.dark.copyWith(statusBarColor: Colors.transparent),
      child: Scaffold(
        body: SafeArea(
          child: Stack(
            children: [
              Positioned(
                top: 4,
                right: 8,
                child: IconButton(
                  tooltip: 'Chiqish',
                  onPressed: _logout,
                  icon: const Icon(Icons.logout, size: 20, color: Color(0xFFB4B9BF)),
                ),
              ),
              LayoutBuilder(
                builder: (context, constraints) {
                  final vertical = constraints.maxWidth < 600;
                  final base = vertical ? kCardBaseSize.flipped : kCardBaseSize;
                  final scale = [
                    (constraints.maxWidth - (vertical ? 64 : 40)) / base.width,
                    (constraints.maxHeight - 140) / base.height,
                    vertical ? 1.35 : 1.12,
                  ].reduce(math.min).clamp(0.35, double.infinity);
                  final cardWidth = base.width * scale;
                  final cardHeight = base.height * scale;

                  Widget face(Widget child) => Container(
                        width: cardWidth,
                        height: cardHeight,
                        decoration: BoxDecoration(
                          borderRadius: BorderRadius.circular(kCardRadius * scale),
                          boxShadow: cardShadow(scale),
                        ),
                        child: RotatedBox(
                          quarterTurns: vertical ? 1 : 0,
                          child: FittedBox(child: child),
                        ),
                      );

                  return Center(
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        if (card.revoked)
                          const Padding(
                            padding: EdgeInsets.only(bottom: 16),
                            child: Text(
                              'Karta bekor qilingan',
                              style: TextStyle(
                                color: Color(0xFFC62828),
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                          ),
                        FlipCard(
                          width: cardWidth,
                          front: face(CardFront(card: card)),
                          back: face(CardBack(card: card)),
                          onSideChanged: (back) => setState(() => _showingBack = back),
                        ),
                        const SizedBox(height: 36),
                        AnimatedSwitcher(
                          duration: const Duration(milliseconds: 200),
                          child: Text(
                            _showingBack ? 'BACK' : 'FRONT',
                            key: ValueKey(_showingBack),
                            style: const TextStyle(
                              color: Color(0xFF9AA0A6),
                              fontSize: 11,
                              fontWeight: FontWeight.w600,
                              letterSpacing: 4,
                            ),
                          ),
                        ),
                        const SizedBox(height: 12),
                        const Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Icon(Icons.swipe, size: 16, color: Color(0xFFB4B9BF)),
                            SizedBox(width: 6),
                            Text(
                              'Aylantirish uchun suring',
                              style: TextStyle(color: Color(0xFFB4B9BF), fontSize: 12),
                            ),
                          ],
                        ),
                      ],
                    ),
                  );
                },
              ),
            ],
          ),
        ),
      ),
    );
  }
}
