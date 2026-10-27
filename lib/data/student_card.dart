import 'package:flutter/foundation.dart';

/// Display model for the on-screen card. The QR encodes [qrPayload] only —
/// never full PII. Access control is decided by the backend verify endpoint.
@immutable
class StudentCard {
  const StudentCard({
    required this.fullName,
    required this.studentId,
    required this.cardId,
    required this.organization,
    required this.access,
    required this.issueDate,
    required this.validUntil,
    required this.qrPayload,
    this.revoked = false,
  });

  final String fullName;
  final String studentId;
  final String cardId;
  final String organization;
  final String access;
  final DateTime issueDate;
  final DateTime validUntil;
  final String qrPayload;
  final bool revoked;

  String get issueDateDisplay => _formatDisplay(issueDate);

  factory StudentCard.fromJson(Map<String, dynamic> json) {
    return StudentCard(
      fullName: json['fullName'] as String,
      studentId: json['studentId'] as String,
      cardId: json['cardId'] as String,
      organization: json['organization'] as String,
      access: json['access'] as String,
      issueDate: DateTime.parse(json['issueDate'] as String),
      validUntil: DateTime.parse(json['validUntil'] as String),
      qrPayload: json['qrPayload'] as String,
      revoked: json['revoked'] as bool? ?? false,
    );
  }

  static String _two(int v) => v.toString().padLeft(2, '0');

  static String _formatDisplay(DateTime d) =>
      '${_two(d.day)} / ${_two(d.month)} / ${d.year}';
}
