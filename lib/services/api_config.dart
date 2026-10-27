/// Backend base URL.
///
/// Android emulator → host machine: `http://10.0.2.2:8000`
/// iOS simulator / desktop / web → `http://127.0.0.1:8000`
/// Physical device → your PC LAN IP, e.g. `http://192.168.1.10:8000`
class ApiConfig {
  static const String baseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://127.0.0.1:8000',
  );
}
