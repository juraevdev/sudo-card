import 'package:flutter/material.dart';

import '../services/ecard_api.dart';
import '../services/session_store.dart';
import '../widgets/card_style.dart';
import 'card_screen.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key, this.api, this.store});

  final EcardApi? api;
  final SessionStore? store;

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _studentId = TextEditingController(text: 'SA-104237');
  final _password = TextEditingController();
  late final EcardApi _api = widget.api ?? EcardApi();
  late final SessionStore _store = widget.store ?? SessionStore();

  bool _loading = false;
  String? _error;

  @override
  void dispose() {
    _studentId.dispose();
    _password.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final token = await _api.login(
        studentId: _studentId.text,
        password: _password.text,
      );
      await _store.saveToken(token);
      final card = await _api.fetchMyCard(token);
      if (!mounted) return;
      Navigator.of(context).pushReplacement(
        MaterialPageRoute(builder: (_) => CardScreen(card: card, store: _store)),
      );
    } on ApiException catch (e) {
      setState(() => _error = e.message);
    } catch (_) {
      setState(() => _error = 'Serverga ulanib bo‘lmadi. Backend ishlayaptimi?');
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Center(
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 360),
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 28),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Text(
                    'UzNext',
                    textAlign: TextAlign.center,
                    style: TextStyle(
                      fontSize: 34,
                      fontWeight: FontWeight.w800,
                      color: CardColors.greenDark,
                      letterSpacing: -0.5,
                    ),
                  ),
                  const SizedBox(height: 8),
                  const Text(
                    'IT Park e-card',
                    textAlign: TextAlign.center,
                    style: TextStyle(color: Color(0xFF8A9099), fontSize: 14),
                  ),
                  const SizedBox(height: 40),
                  TextField(
                    controller: _studentId,
                    textInputAction: TextInputAction.next,
                    decoration: const InputDecoration(
                      labelText: 'Student ID',
                      border: OutlineInputBorder(),
                    ),
                  ),
                  const SizedBox(height: 14),
                  TextField(
                    controller: _password,
                    obscureText: true,
                    onSubmitted: (_) => _loading ? null : _submit(),
                    decoration: const InputDecoration(
                      labelText: 'Parol',
                      border: OutlineInputBorder(),
                    ),
                  ),
                  if (_error != null) ...[
                    const SizedBox(height: 14),
                    Text(
                      _error!,
                      style: const TextStyle(color: Color(0xFFC62828), fontSize: 13),
                    ),
                  ],
                  const SizedBox(height: 22),
                  FilledButton(
                    onPressed: _loading ? null : _submit,
                    style: FilledButton.styleFrom(
                      backgroundColor: CardColors.greenDark,
                      padding: const EdgeInsets.symmetric(vertical: 14),
                    ),
                    child: _loading
                        ? const SizedBox(
                            width: 20,
                            height: 20,
                            child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                          )
                        : const Text('Kirish'),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
