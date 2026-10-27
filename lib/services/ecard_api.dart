import 'dart:convert';

import 'package:http/http.dart' as http;

import '../data/student_card.dart';
import 'api_config.dart';

class ApiException implements Exception {
  ApiException(this.message, {this.statusCode});

  final String message;
  final int? statusCode;

  @override
  String toString() => message;
}

class EcardApi {
  EcardApi({http.Client? client, String? baseUrl})
      : _client = client ?? http.Client(),
        _baseUrl = baseUrl ?? ApiConfig.baseUrl;

  final http.Client _client;
  final String _baseUrl;

  Future<String> login({
    required String studentId,
    required String password,
  }) async {
    final res = await _client.post(
      Uri.parse('$_baseUrl/auth/login'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'studentId': studentId.trim(),
        'password': password,
      }),
    );
    final body = _decode(res);
    if (res.statusCode != 200) {
      throw ApiException(
        body['detail']?.toString() ?? 'Login failed',
        statusCode: res.statusCode,
      );
    }
    return body['accessToken'] as String;
  }

  Future<StudentCard> fetchMyCard(String accessToken) async {
    final res = await _client.get(
      Uri.parse('$_baseUrl/card/me'),
      headers: {'Authorization': 'Bearer $accessToken'},
    );
    final body = _decode(res);
    if (res.statusCode != 200) {
      throw ApiException(
        body['detail']?.toString() ?? 'Could not load card',
        statusCode: res.statusCode,
      );
    }
    return StudentCard.fromJson(body);
  }

  Map<String, dynamic> _decode(http.Response res) {
    if (res.body.isEmpty) return <String, dynamic>{};
    final decoded = jsonDecode(res.body);
    if (decoded is Map<String, dynamic>) return decoded;
    if (decoded is Map) return Map<String, dynamic>.from(decoded);
    return <String, dynamic>{'detail': res.body};
  }
}
