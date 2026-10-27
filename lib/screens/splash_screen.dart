import 'package:flutter/material.dart';

import '../services/ecard_api.dart';
import '../services/session_store.dart';
import '../widgets/card_style.dart';
import 'card_screen.dart';
import 'login_screen.dart';

class SplashScreen extends StatefulWidget {
  const SplashScreen({super.key, this.api, this.store});

  final EcardApi? api;
  final SessionStore? store;

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen> {
  @override
  void initState() {
    super.initState();
    _bootstrap();
  }

  Future<void> _bootstrap() async {
    final store = widget.store ?? SessionStore();
    final api = widget.api ?? EcardApi();
    final token = await store.readToken();
    if (!mounted) return;

    if (token == null) {
      _go(const LoginScreen());
      return;
    }

    try {
      final card = await api.fetchMyCard(token);
      if (!mounted) return;
      _go(CardScreen(card: card, store: store));
    } catch (_) {
      await store.clear();
      if (!mounted) return;
      _go(const LoginScreen());
    }
  }

  void _go(Widget page) {
    Navigator.of(context).pushReplacement(
      MaterialPageRoute(builder: (_) => page),
    );
  }

  @override
  Widget build(BuildContext context) {
    return const Scaffold(
      body: Center(
        child: CircularProgressIndicator(color: CardColors.greenDark),
      ),
    );
  }
}
