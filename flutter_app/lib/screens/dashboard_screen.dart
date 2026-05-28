import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:percent_indicator/percent_indicator.dart';
import '../services/api_service.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  Map<String, dynamic>? _stats;
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _loadStats();
  }

  Future<void> _loadStats() async {
    setState(() => _loading = true);
    final stats = await ApiService().getDashboardStats();
    setState(() {
      _stats = stats;
      _loading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0A1628),
      body: RefreshIndicator(
        onRefresh: _loadStats,
        color: const Color(0xFFFFB800),
        child: CustomScrollView(
          slivers: [
            SliverAppBar(
              expandedHeight: 120,
              floating: false,
              pinned: true,
              backgroundColor: const Color(0xFF0D2144),
              flexibleSpace: FlexibleSpaceBar(
                title: Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.all(6),
                      decoration: BoxDecoration(
                        gradient: const LinearGradient(
                          colors: [Color(0xFFFFB800), Color(0xFFFF8C00)],
                        ),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: const Text('🏦', style: TextStyle(fontSize: 16)),
                    ),
                    const SizedBox(width: 10),
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Text('SuRaksha',
                            style: GoogleFonts.inter(
                                fontSize: 16, fontWeight: FontWeight.w800, color: Colors.white)),
                        Text('Compliance Center',
                            style: GoogleFonts.inter(fontSize: 10, color: const Color(0xFF94A3B8))),
                      ],
                    ),
                  ],
                ),
                titlePadding: const EdgeInsets.only(left: 16, bottom: 12),
              ),
              actions: [
                IconButton(
                  icon: const Icon(Icons.refresh_rounded, color: Color(0xFFFFB800)),
                  onPressed: _loadStats,
                ),
                const SizedBox(width: 8),
              ],
            ),
            if (_loading)
              const SliverFillRemaining(
                child: Center(
                  child: CircularProgressIndicator(color: Color(0xFFFFB800)),
                ),
              )
            else if (_stats == null)
              SliverFillRemaining(
                child: Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      const Icon(Icons.wifi_off_rounded, size: 48, color: Color(0xFF64748B)),
                      const SizedBox(height: 16),
                      Text('Could not connect to API',
                          style: GoogleFonts.inter(color: const Color(0xFF64748B))),
                      const SizedBox(height: 16),
                      ElevatedButton(onPressed: _loadStats, child: const Text('Retry')),
                    ],
                  ),
                ),
              )
            else
              SliverPadding(
                padding: const EdgeInsets.all(16),
                sliver: SliverList(
                  delegate: SliverChildListDelegate([
                    _buildComplianceGauge(),
                    const SizedBox(height: 16),
                    _buildKpiGrid(),
                    const SizedBox(height: 16),
                    _buildSectionTitle('📊 MAP Status'),
                    const SizedBox(height: 8),
                    _buildStatusChart(),
                    const SizedBox(height: 16),
                    _buildSectionTitle('🏢 Department Scores'),
                    const SizedBox(height: 8),
                    _buildDepartmentList(),
                    const SizedBox(height: 16),
                    _buildSectionTitle('📋 Recent Regulations'),
                    const SizedBox(height: 8),
                    _buildRecentRegs(),
                    const SizedBox(height: 80),
                  ]),
                ),
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildComplianceGauge() {
    final score = (_stats!['compliance_score'] as num?)?.toDouble() ?? 0;
    final color = score >= 75
        ? const Color(0xFF22C55E)
        : score >= 50
            ? const Color(0xFFF59E0B)
            : const Color(0xFFEF4444);

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            const Color(0xFF0D2144),
            color.withOpacity(0.1),
          ],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Column(
        children: [
          Text('Overall Compliance Score',
              style: GoogleFonts.inter(
                  fontSize: 13, color: const Color(0xFF94A3B8), fontWeight: FontWeight.w500)),
          const SizedBox(height: 16),
          CircularPercentIndicator(
            radius: 80,
            lineWidth: 12,
            percent: score / 100,
            center: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Text('${score.toStringAsFixed(1)}%',
                    style: GoogleFonts.inter(
                        fontSize: 28, fontWeight: FontWeight.w800, color: Colors.white)),
                Text('Score', style: GoogleFonts.inter(fontSize: 11, color: const Color(0xFF64748B))),
              ],
            ),
            progressColor: color,
            backgroundColor: const Color(0xFF1E3A5F),
            circularStrokeCap: CircularStrokeCap.round,
            animation: true,
            animationDuration: 1200,
          ),
        ],
      ),
    );
  }

  Widget _buildKpiGrid() {
    final s = _stats!;
    final kpis = [
      {'label': 'Regulations', 'value': '${s['total_regulations'] ?? 0}', 'icon': '📜', 'color': const Color(0xFF3B82F6)},
      {'label': 'Total MAPs', 'value': '${s['total_maps'] ?? 0}', 'icon': '📌', 'color': const Color(0xFF8B5CF6)},
      {'label': 'Completed', 'value': '${s['completed_maps'] ?? 0}', 'icon': '✅', 'color': const Color(0xFF22C55E)},
      {'label': 'Overdue', 'value': '${s['overdue_maps'] ?? 0}', 'icon': '⚠️', 'color': const Color(0xFFEF4444)},
      {'label': 'Alerts', 'value': '${s['active_alerts'] ?? 0}', 'icon': '🚨', 'color': const Color(0xFFEA580C)},
      {'label': 'In Progress', 'value': '${s['in_progress_maps'] ?? 0}', 'icon': '🔄', 'color': const Color(0xFF0EA5E9)},
    ];

    return GridView.count(
      crossAxisCount: 3,
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      crossAxisSpacing: 10,
      mainAxisSpacing: 10,
      childAspectRatio: 1.1,
      children: kpis.map((kpi) => _buildKpiCard(kpi)).toList(),
    );
  }

  Widget _buildKpiCard(Map kpi) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: const Color(0xFF0F1E35),
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: (kpi['color'] as Color).withOpacity(0.25)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(kpi['icon'] as String, style: const TextStyle(fontSize: 22)),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(kpi['value'] as String,
                  style: GoogleFonts.inter(
                      fontSize: 22, fontWeight: FontWeight.w800, color: Colors.white)),
              Text(kpi['label'] as String,
                  style: GoogleFonts.inter(
                      fontSize: 10, color: const Color(0xFF64748B), fontWeight: FontWeight.w500)),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildStatusChart() {
    final s = _stats!;
    final data = [
      FlSpot(0, (s['pending_maps'] as num?)?.toDouble() ?? 0),
      FlSpot(1, (s['in_progress_maps'] as num?)?.toDouble() ?? 0),
      FlSpot(2, (s['completed_maps'] as num?)?.toDouble() ?? 0),
      FlSpot(3, (s['overdue_maps'] as num?)?.toDouble() ?? 0),
    ];

    return Container(
      height: 180,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF0F1E35),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFF1E3A5F)),
      ),
      child: BarChart(
        BarChartData(
          alignment: BarChartAlignment.spaceAround,
          maxY: ((s['total_maps'] as num?)?.toDouble() ?? 10) + 2,
          barGroups: [
            _barGroup(0, (s['pending_maps'] as num?)?.toDouble() ?? 0, const Color(0xFF64748B)),
            _barGroup(1, (s['in_progress_maps'] as num?)?.toDouble() ?? 0, const Color(0xFF3B82F6)),
            _barGroup(2, (s['completed_maps'] as num?)?.toDouble() ?? 0, const Color(0xFF22C55E)),
            _barGroup(3, (s['overdue_maps'] as num?)?.toDouble() ?? 0, const Color(0xFFEF4444)),
          ],
          titlesData: FlTitlesData(
            bottomTitles: AxisTitles(
              sideTitles: SideTitles(
                showTitles: true,
                getTitlesWidget: (v, _) {
                  const titles = ['Pending', 'In Progress', 'Done', 'Overdue'];
                  return Padding(
                    padding: const EdgeInsets.only(top: 6),
                    child: Text(titles[v.toInt()],
                        style: GoogleFonts.inter(fontSize: 9, color: const Color(0xFF64748B))),
                  );
                },
              ),
            ),
            leftTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
            topTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
            rightTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
          ),
          gridData: FlGridData(
            show: true,
            getDrawingHorizontalLine: (_) => FlLine(color: const Color(0xFF1E3A5F), strokeWidth: 1),
            drawVerticalLine: false,
          ),
          borderData: FlBorderData(show: false),
        ),
      ),
    );
  }

  BarChartGroupData _barGroup(int x, double y, Color color) {
    return BarChartGroupData(
      x: x,
      barRods: [
        BarChartRodData(
          toY: y,
          color: color,
          width: 32,
          borderRadius: BorderRadius.circular(6),
        ),
      ],
    );
  }

  Widget _buildDepartmentList() {
    final depts = (_stats!['department_breakdown'] as List?) ?? [];
    return Column(
      children: depts.map<Widget>((d) {
        final score = (d['score'] as num?)?.toDouble() ?? 0;
        final color = score >= 75
            ? const Color(0xFF22C55E)
            : score >= 50
                ? const Color(0xFFF59E0B)
                : const Color(0xFFEF4444);
        return Container(
          margin: const EdgeInsets.only(bottom: 8),
          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
          decoration: BoxDecoration(
            color: const Color(0xFF0F1E35),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: const Color(0xFF1E3A5F)),
          ),
          child: Row(
            children: [
              Expanded(
                flex: 2,
                child: Text(d['department'] ?? '',
                    style: GoogleFonts.inter(
                        fontWeight: FontWeight.w600, color: Colors.white, fontSize: 13)),
              ),
              Expanded(
                flex: 3,
                child: LinearProgressIndicator(
                  value: score / 100,
                  backgroundColor: const Color(0xFF1E3A5F),
                  valueColor: AlwaysStoppedAnimation(color),
                  borderRadius: BorderRadius.circular(999),
                  minHeight: 8,
                ),
              ),
              const SizedBox(width: 10),
              Text('${score.toStringAsFixed(1)}%',
                  style: GoogleFonts.inter(
                      fontWeight: FontWeight.w700, color: color, fontSize: 13)),
            ],
          ),
        );
      }).toList(),
    );
  }

  Widget _buildRecentRegs() {
    final regs = (_stats!['recent_regulations'] as List?) ?? [];
    final srcColors = {
      'RBI': const Color(0xFF1D4ED8),
      'SEBI': const Color(0xFF7C3AED),
      'EU-GDPR': const Color(0xFF059669),
    };
    return Column(
      children: regs.map<Widget>((r) {
        final src = r['source'] ?? '';
        final color = srcColors[src] ?? const Color(0xFF475569);
        return Container(
          margin: const EdgeInsets.only(bottom: 8),
          padding: const EdgeInsets.all(14),
          decoration: BoxDecoration(
            color: const Color(0xFF0F1E35),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: const Color(0xFF1E3A5F)),
          ),
          child: Row(
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      (r['title'] ?? '').toString().length > 50
                          ? '${r['title'].toString().substring(0, 50)}…'
                          : r['title'] ?? '',
                      style: GoogleFonts.inter(
                          fontWeight: FontWeight.w600, color: Colors.white, fontSize: 12),
                    ),
                    const SizedBox(height: 4),
                    Text(r['created_at']?.toString().substring(0, 10) ?? '',
                        style: GoogleFonts.inter(fontSize: 10, color: const Color(0xFF64748B))),
                  ],
                ),
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                decoration: BoxDecoration(
                  color: color,
                  borderRadius: BorderRadius.circular(999),
                ),
                child: Text(src,
                    style: GoogleFonts.inter(
                        fontSize: 10, fontWeight: FontWeight.w700, color: Colors.white)),
              ),
            ],
          ),
        );
      }).toList(),
    );
  }

  Widget _buildSectionTitle(String title) {
    return Text(title,
        style: GoogleFonts.inter(
            fontSize: 16, fontWeight: FontWeight.w700, color: Colors.white));
  }
}
