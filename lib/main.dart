import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import 'screens/splash_screen.dart';
import 'widgets/card_style.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await SystemChrome.setPreferredOrientations([DeviceOrientation.portraitUp]);
  runApp(const SudoECardApp());
}

class SudoECardApp extends StatelessWidget {
  const SudoECardApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'UzNext E-Card',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        scaffoldBackgroundColor: Colors.white,
        colorScheme: ColorScheme.fromSeed(seedColor: CardColors.green),
      ),
      home: const SplashScreen(),
    );
  }
}
