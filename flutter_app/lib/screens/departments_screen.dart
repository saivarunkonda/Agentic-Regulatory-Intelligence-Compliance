import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:percent_indicator/percent_indicator.dart';
import '../services/api_service.dart';

class DepartmentsScreen extends StatefulWidget {
  const DepartmentsScreen({super.key});

  @override
  State<DepartmentsScreen> createState() => _DepartmentsScreenState();
}

class _DepartmentsScreenState extends State<DepartmentsScreen> {
  List<dynamic> _depts = [];
  bool _loading = true;

  final _icons = {'Legal': '⚖️', 'Risk': '🛡️', 'IT': '💻', 'Operations': '⚙️', 'Audit': '🔍'};
  final _colors = {
    'Legal': const Color(0xFF7C3AED),
    'Risk': const Color(0xFFDC2626),
    'IT': const Color(0xFF2563EB),
    'Operations': const Color(0xFF0891B2),
    'Audit': const Color(0xFF059669),
  };

  @override
  void initState() {
    super.initState();
    _loadDepts();
  }

  Future<void> _loadDepts() async {
    setState(() => _loading = true);
    final depts = await ApiService().getDepartments();
    depts.sort((a, b) =>
        (b['compliance_score'] as num).compareTo(a['compliance_score'] as num));
    setState(() {
      _depts = depts;
      _loading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0A1628),
      appBar: AppBar(
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Departments', style: GoogleFonts.inter(fontWeight: FontWeight.w800, fontSize: 18)),
            Text('Compliance Leaderboard',
                style: GoogleFonts.inter(fontSize: 11, color: const Color(0xFF94A3B8))),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh_rounded, color: Color(0xFFFFB800)),
            onPressed: _loadDepts,
          ),
        ],
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator(color: Color(0xFFFFB800)))
          : RefreshIndicator(
              onRefresh: _loadDepts,
              color: const Color(0xFFFFB800),
              child: ListView(
                padding: const EdgeInsets.all(16),
                children: [
                  // ── Podium ────────────────────────────────────────────
                  if (_depts.length >= 3) _buildPodium(),
                  const SizedBox(height: 20),
                  Text('All Departments',
                      style: GoogleFonts.inter(
                          fontWeight: FontWeight.w700, color: Colors.white, fontSize: 16)),
                  const SizedBox(height: 12),
                  ..._depts.asMap().entries.map((e) => _buildDeptCard(e.key, e.value)),
                  const SizedBox(height: 80),
                ],
              ),
            ),
    );
  }

  Widget _buildPodium() {
    final medals = ['🥇', '🥈', '🥉'];
    return Row(
      crossAxisAlignment: CrossAxisAlignment.end,
      children: [
        // 2nd place
        Expanded(child: _podiumBlock(_depts[1], medals[1], 80)),
        const SizedBox(width: 8),
        // 1st place
        Expanded(child: _podiumBlock(_depts[0], medals[0], 110)),
        const SizedBox(width: 8),
        // 3rd place
        Expanded(child: _podiumBlock(_depts[2], medals[2], 60)),
      ],
    );
  }

  Widget _podiumBlock(Map dept, String medal, double height) {
    final name = dept['name'] ?? '';
    final score = (dept['compliance_score'] as num?)?.toDouble() ?? 0;
    final color = _colors[name] ?? const Color(0xFF475569);
    final icon = _icons[name] ?? '🏦';
    final scoreColor = score >= 75
        ? const Color(0xFF22C55E)
        : score >= 50
            ? const Color(0xFFF59E0B)
            : const Color(0xFFEF4444);

    return Column(
      children: [
        Text(icon, style: const TextStyle(fontSize: 28)),
        const SizedBox(height: 4),
        Text(medal, style: const TextStyle(fontSize: 20)),
        const SizedBox(height: 4),
        Text(name,
            textAlign: TextAlign.center,
            style: GoogleFonts.inter(
                fontSize: 11, fontWeight: FontWeight.w700, color: Colors.white)),
        const SizedBox(height: 2),
        Text('${score.toStringAsFixed(1)}%',
            style: GoogleFonts.inter(
                fontSize: 13, fontWeight: FontWeight.w800, color: scoreColor)),
        const SizedBox(height: 6),
        Container(
          height: height,
          decoration: BoxDecoration(
            color: color.withOpacity(0.2),
            borderRadius: const BorderRadius.vertical(top: Radius.circular(10)),
            border: Border.all(color: color.withOpacity(0.5)),
          ),
        ),
      ],
    );
  }

  Widget _buildDeptCard(int rank, Map dept) {
    final name = dept['name'] ?? '';
    final score = (dept['compliance_score'] as num?)?.toDouble() ?? 0;
    final color = _colors[name] ?? const Color(0xFF475569);
    final icon = _icons[name] ?? '🏦';
    final mapCounts = dept['map_counts'] as Map? ?? {};
    final total = mapCounts.values.fold<int>(0, (a, b) => a + (b as int));
    final completed = mapCounts['completed'] ?? 0;
    final inProgress = mapCounts['in_progress'] ?? 0;
    final pending = mapCounts['pending'] ?? 0;
    final scoreColor = score >= 75
        ? const Color(0xFF22C55E)
        : score >= 50
            ? const Color(0xFFF59E0B)
            : const Color(0xFFEF4444);

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF0F1E35),
        borderRadius: BorderRadius.circular(16),
        border: Border(left: BorderSide(color: color, width: 4)),
      ),
      child: Column(
        children: [
          Row(
            children: [
              Text('${rank + 1}.',
                  style: GoogleFonts.inter(
                      fontSize: 13, fontWeight: FontWeight.w700, color: const Color(0xFF64748B))),
              const SizedBox(width: 8),
              Text(icon, style: const TextStyle(fontSize: 24)),
              const SizedBox(width: 10),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(name,
                        style: GoogleFonts.inter(
                            fontSize: 15, fontWeight: FontWeight.w800, color: Colors.white)),
                    Text(dept['head'] ?? '',
                        style: GoogleFonts.inter(fontSize: 11, color: const Color(0xFF64748B))),
                  ],
                ),
              ),
              CircularPercentIndicator(
                radius: 30,
                lineWidth: 5,
                percent: score / 100,
                center: Text('${score.toStringAsFixed(0)}%',
                    style: GoogleFonts.inter(
                        fontSize: 9, fontWeight: FontWeight.w800, color: scoreColor)),
                progressColor: scoreColor,
                backgroundColor: const Color(0xFF1E3A5F),
                circularStrokeCap: CircularStrokeCap.round,
                animation: true,
              ),
            ],
          ),
          const SizedBox(height: 12),
          ClipRRect(
            borderRadius: BorderRadius.circular(999),
            child: LinearProgressIndicator(
              value: total > 0 ? completed / total : 0,
              backgroundColor: const Color(0xFF1E3A5F),
              valueColor: AlwaysStoppedAnimation(scoreColor),
              minHeight: 6,
            ),
          ),
          const SizedBox(height: 10),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _mapStat('✅ Done', '$completed', const Color(0xFF22C55E)),
              _mapStat('🔄 Active', '$inProgress', const Color(0xFF3B82F6)),
              _mapStat('⏳ Pending', '$pending', const Color(0xFF64748B)),
              _mapStat('📌 Total', '$total', color),
            ],
          ),
          const SizedBox(height: 6),
          Text(dept['contact'] ?? '',
              style: GoogleFonts.inter(fontSize: 10, color: const Color(0xFF475569))),
        ],
      ),
    );
  }

  Widget _mapStat(String label, String value, Color color) => Column(
        children: [
          Text(value,
              style: GoogleFonts.inter(
                  fontSize: 16, fontWeight: FontWeight.w800, color: color)),
          Text(label,
              style: GoogleFonts.inter(fontSize: 9, color: const Color(0xFF64748B))),
        ],
      );
}
