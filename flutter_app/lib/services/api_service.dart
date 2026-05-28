import 'dart:convert';
import 'package:http/http.dart' as http;

const String baseUrl = 'http://10.0.2.2:8000'; // Android emulator → localhost
// Use 'http://localhost:8000' for web/desktop

class ApiService {
  static final ApiService _instance = ApiService._internal();
  factory ApiService() => _instance;
  ApiService._internal();

  Future<Map<String, dynamic>?> getDashboardStats() async {
    return await _get('/dashboard/stats');
  }

  Future<List<dynamic>> getRegulations({String? source}) async {
    final params = source != null ? '?source=$source' : '';
    final result = await _get('/regulations$params');
    return result is List ? result : [];
  }

  Future<List<dynamic>> getMaps({String? department, String? status, String? priority}) async {
    final params = <String, String>{};
    if (department != null) params['department'] = department;
    if (status != null) params['status'] = status;
    if (priority != null) params['priority'] = priority;
    final query = params.isNotEmpty
        ? '?' + params.entries.map((e) => '${e.key}=${e.value}').join('&')
        : '';
    final result = await _get('/maps$query');
    return result is List ? result : [];
  }

  Future<Map<String, dynamic>?> getMapDetail(int id) async {
    return await _get('/maps/$id');
  }

  Future<List<dynamic>> getDepartments() async {
    final result = await _get('/departments');
    return result is List ? result : [];
  }

  Future<List<dynamic>> getAlerts({bool resolved = false}) async {
    final result = await _get('/alerts?resolved=${resolved ? 1 : 0}');
    return result is List ? result : [];
  }

  Future<Map<String, dynamic>?> generateMaps(int regulationId) async {
    return await _post('/maps/generate/$regulationId', {});
  }

  Future<Map<String, dynamic>?> updateMapStatus(
      int mapId, String status, String actor, String notes) async {
    return await _patch('/maps/$mapId/status', {
      'status': status,
      'actor': actor,
      'notes': notes,
    });
  }

  Future<Map<String, dynamic>?> validateMap(int mapId) async {
    return await _post('/validate/$mapId', {});
  }

  Future<Map<String, dynamic>?> ingestText(
      String title, String source, String text) async {
    return await _post('/regulations/ingest/text', {
      'title': title,
      'source': source,
      'text': text,
    });
  }

  Future<Map<String, dynamic>?> resolveAlert(int alertId) async {
    return await _patch('/alerts/$alertId/resolve', {});
  }

  // ── Private helpers ───────────────────────────────────────────────────────

  Future<dynamic> _get(String endpoint) async {
    try {
      final response = await http
          .get(Uri.parse('$baseUrl$endpoint'))
          .timeout(const Duration(seconds: 10));
      if (response.statusCode == 200) {
        return json.decode(response.body);
      }
      return null;
    } catch (e) {
      return null;
    }
  }

  Future<Map<String, dynamic>?> _post(String endpoint, Map<String, dynamic> body) async {
    try {
      final response = await http
          .post(
            Uri.parse('$baseUrl$endpoint'),
            headers: {'Content-Type': 'application/json'},
            body: json.encode(body),
          )
          .timeout(const Duration(seconds: 15));
      if (response.statusCode == 200) {
        return json.decode(response.body);
      }
      return null;
    } catch (e) {
      return null;
    }
  }

  Future<Map<String, dynamic>?> _patch(String endpoint, Map<String, dynamic> body) async {
    try {
      final response = await http
          .patch(
            Uri.parse('$baseUrl$endpoint'),
            headers: {'Content-Type': 'application/json'},
            body: json.encode(body),
          )
          .timeout(const Duration(seconds: 10));
      if (response.statusCode == 200) {
        return json.decode(response.body);
      }
      return null;
    } catch (e) {
      return null;
    }
  }
}
