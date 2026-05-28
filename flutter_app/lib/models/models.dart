import 'package:flutter/material.dart';

class RegulationModel {
  final int id;
  final String title;
  final String source;
  final String url;
  final String rawText;
  final String status;
  final String createdAt;

  RegulationModel({
    required this.id,
    required this.title,
    required this.source,
    required this.url,
    required this.rawText,
    required this.status,
    required this.createdAt,
  });

  factory RegulationModel.fromJson(Map<String, dynamic> j) => RegulationModel(
        id: j['id'] ?? 0,
        title: j['title'] ?? '',
        source: j['source'] ?? '',
        url: j['url'] ?? '',
        rawText: j['raw_text'] ?? '',
        status: j['status'] ?? 'new',
        createdAt: j['created_at'] ?? '',
      );
}

class MapModel {
  final int id;
  final int regulationId;
  final String title;
  final String description;
  final String priority;
  final String department;
  final String deadline;
  final String status;
  final String? evidenceUrl;
  final String createdAt;

  MapModel({
    required this.id,
    required this.regulationId,
    required this.title,
    required this.description,
    required this.priority,
    required this.department,
    required this.deadline,
    required this.status,
    this.evidenceUrl,
    required this.createdAt,
  });

  factory MapModel.fromJson(Map<String, dynamic> j) => MapModel(
        id: j['id'] ?? 0,
        regulationId: j['regulation_id'] ?? 0,
        title: j['title'] ?? '',
        description: j['description'] ?? '',
        priority: j['priority'] ?? 'medium',
        department: j['department'] ?? '',
        deadline: j['deadline'] ?? '',
        status: j['status'] ?? 'pending',
        evidenceUrl: j['evidence_url'],
        createdAt: j['created_at'] ?? '',
      );

  Color get priorityColor {
    switch (priority) {
      case 'critical': return const Color(0xFFDC2626);
      case 'high':     return const Color(0xFFEA580C);
      case 'medium':   return const Color(0xFFCA8A04);
      case 'low':      return const Color(0xFF16A34A);
      default:         return const Color(0xFF64748B);
    }
  }

  Color get statusColor {
    switch (status) {
      case 'completed':   return const Color(0xFF16A34A);
      case 'in_progress': return const Color(0xFF2563EB);
      case 'overdue':     return const Color(0xFFDC2626);
      case 'escalated':   return const Color(0xFF9333EA);
      default:            return const Color(0xFF64748B);
    }
  }
}

class DepartmentModel {
  final int id;
  final String name;
  final String head;
  final String contact;
  final double complianceScore;
  final Map<String, int> mapCounts;

  DepartmentModel({
    required this.id,
    required this.name,
    required this.head,
    required this.contact,
    required this.complianceScore,
    required this.mapCounts,
  });

  factory DepartmentModel.fromJson(Map<String, dynamic> j) => DepartmentModel(
        id: j['id'] ?? 0,
        name: j['name'] ?? '',
        head: j['head'] ?? '',
        contact: j['contact'] ?? '',
        complianceScore: (j['compliance_score'] ?? 0).toDouble(),
        mapCounts: Map<String, int>.from(j['map_counts'] ?? {}),
      );
}

class AlertModel {
  final int id;
  final int mapId;
  final String type;
  final String message;
  final String createdAt;
  final bool resolved;

  AlertModel({
    required this.id,
    required this.mapId,
    required this.type,
    required this.message,
    required this.createdAt,
    required this.resolved,
  });

  factory AlertModel.fromJson(Map<String, dynamic> j) => AlertModel(
        id: j['id'] ?? 0,
        mapId: j['map_id'] ?? 0,
        type: j['type'] ?? '',
        message: j['message'] ?? '',
        createdAt: j['created_at'] ?? '',
        resolved: (j['resolved'] ?? 0) == 1,
      );
}
