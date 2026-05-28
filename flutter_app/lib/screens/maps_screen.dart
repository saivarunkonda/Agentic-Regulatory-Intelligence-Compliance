import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../services/api_service.dart';
import 'map_detail_screen.dart';

class MapsScreen extends StatefulWidget {
  const MapsScreen({super.key});

  @override
  State<MapsScreen> createState() => _MapsScreenState();
}

class _MapsScreenState extends State<MapsScreen> with SingleTickerProviderStateMixin {
  List<dynamic> _maps = [];
  bool _loading = true;
  String _deptFilter = 'All';
  String _statusFilter = 'All';
  String _priorityFilter = 'All';
  late TabController _tabController;

  final _depts = ['All', 'Legal', 'Risk', 'IT', 'Operations', 'Audit'];
  final _statuses = ['All', 'pending', 'in_progress', 'completed', 'overdue'];
  final _priorities = ['All', 'critical', 'high', 'medium', 'low'];

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 4, vsync: this);
    _loadMaps();
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  Future<void> _loadMaps() async {
    setState(() => _loading = true);
    final maps = await ApiService().getMaps(
      department: _deptFilter == 'All' ? null : _deptFilter,
      status: _statusFilter == 'All' ? null : _statusFilter,
      priority: _priorityFilter == 'All' ? null : _priorityFilter,
    );
    setState(() {
      _maps = maps;
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
            Text('MAPs', style: GoogleFonts.inter(fontWeight: FontWeight.w800, fontSize: 18)),
            Text('Measurable Action Points',
                style: GoogleFonts.inter(fontSize: 11, color: const Color(0xFF94A3B8))),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh_rounded, color: Color(0xFFFFB800)),
            onPressed: _loadMaps,
          ),
        ],
      ),
      body: Column(
        children: [
          // ── Filters ─────────────────────────────────────────────────────
          Container(
            color: const Color(0xFF0D2144),
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
            child: SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              child: Row(
                children: [
                  _filterChip('Dept', _depts, _deptFilter, (v) {
                    setState(() => _deptFilter = v);
                    _loadMaps();
                  }),
                  const SizedBox(width: 8),
                  _filterChip('Status', _statuses, _statusFilter, (v) {
                    setState(() => _statusFilter = v);
                    _loadMaps();
                  }),
                  const SizedBox(width: 8),
                  _filterChip('Priority', _priorities, _priorityFilter, (v) {
                    setState(() => _priorityFilter = v);
                    _loadMaps();
                  }),
                ],
              ),
            ),
          ),

          // ── Stats Strip ──────────────────────────────────────────────────
          if (!_loading)
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
              child: Row(
                children: [
                  _statPill('Total', '${_maps.length}', const Color(0xFF64748B)),
                  const SizedBox(width: 8),
                  _statPill('Done', '${_maps.where((m) => m['status'] == 'completed').length}', const Color(0xFF22C55E)),
                  const SizedBox(width: 8),
                  _statPill('🔴 Critical', '${_maps.where((m) => m['priority'] == 'critical').length}', const Color(0xFFDC2626)),
                  const SizedBox(width: 8),
                  _statPill('Overdue', '${_maps.where((m) => m['status'] == 'overdue').length}', const Color(0xFFEA580C)),
                ],
              ),
            ),

          // ── MAP List ─────────────────────────────────────────────────────
          Expanded(
            child: _loading
                ? const Center(child: CircularProgressIndicator(color: Color(0xFFFFB800)))
                : _maps.isEmpty
                    ? Center(
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            const Icon(Icons.task_alt_outlined, size: 48, color: Color(0xFF1E3A5F)),
                            const SizedBox(height: 12),
                            Text('No MAPs found',
                                style: GoogleFonts.inter(color: const Color(0xFF64748B))),
                          ],
                        ),
                      )
                    : RefreshIndicator(
                        onRefresh: _loadMaps,
                        color: const Color(0xFFFFB800),
                        child: ListView.separated(
                          padding: const EdgeInsets.all(12),
                          itemCount: _maps.length,
                          separatorBuilder: (_, __) => const SizedBox(height: 8),
                          itemBuilder: (context, i) => _buildMapCard(_maps[i]),
                        ),
                      ),
          ),
        ],
      ),
    );
  }

  Widget _buildMapCard(Map map) {
    final priority = map['priority'] ?? 'medium';
    final status = map['status'] ?? 'pending';

    final priorityColors = {
      'critical': const Color(0xFFDC2626),
      'high': const Color(0xFFEA580C),
      'medium': const Color(0xFFCA8A04),
      'low': const Color(0xFF16A34A),
    };
    final statusColors = {
      'completed': const Color(0xFF22C55E),
      'in_progress': const Color(0xFF3B82F6),
      'pending': const Color(0xFF64748B),
      'overdue': const Color(0xFFEF4444),
    };
    final pColor = priorityColors[priority] ?? const Color(0xFF64748B);
    final sColor = statusColors[status] ?? const Color(0xFF64748B);

    return GestureDetector(
      onTap: () => Navigator.push(
        context,
        MaterialPageRoute(builder: (_) => MapDetailScreen(mapId: map['id'])),
      ),
      child: Container(
        padding: const EdgeInsets.all(14),
        decoration: BoxDecoration(
          color: const Color(0xFF0F1E35),
          borderRadius: BorderRadius.circular(14),
          border: Border(left: BorderSide(color: pColor, width: 4)),
          boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.15), blurRadius: 8)],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(
                  child: Text(
                    map['title'] ?? '',
                    style: GoogleFonts.inter(
                      fontWeight: FontWeight.w700,
                      fontSize: 13,
                      color: Colors.white,
                    ),
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
                Text('#${map['id']}',
                    style: GoogleFonts.inter(fontSize: 10, color: const Color(0xFF475569))),
              ],
            ),
            const SizedBox(height: 6),
            Text(
              (map['description'] ?? '').toString().length > 100
                  ? '${map['description'].toString().substring(0, 100)}…'
                  : map['description'] ?? '',
              style: GoogleFonts.inter(fontSize: 11, color: const Color(0xFF94A3B8)),
            ),
            const SizedBox(height: 10),
            Row(
              children: [
                _tagChip(priority.toUpperCase(), pColor),
                const SizedBox(width: 6),
                _tagChip(status.replaceAll('_', ' ').toUpperCase(), sColor),
                const SizedBox(width: 6),
                _tagChip('🏢 ${map['department'] ?? ''}', const Color(0xFF2563EB)),
                const Spacer(),
                Text('📅 ${map['deadline'] ?? 'N/A'}',
                    style: GoogleFonts.inter(fontSize: 10, color: const Color(0xFF64748B))),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _filterChip(String label, List<String> options, String current, Function(String) onSelect) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: const Color(0xFF0F1E35),
        borderRadius: BorderRadius.circular(999),
        border: Border.all(color: const Color(0xFF1E3A5F)),
      ),
      child: GestureDetector(
        onTap: () => showModalBottomSheet(
          context: context,
          backgroundColor: const Color(0xFF0D2144),
          shape: const RoundedRectangleBorder(
            borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
          ),
          builder: (_) => ListView(
            shrinkWrap: true,
            padding: const EdgeInsets.all(16),
            children: options.map((o) => ListTile(
              title: Text(o, style: GoogleFonts.inter(color: Colors.white)),
              trailing: o == current
                  ? const Icon(Icons.check, color: Color(0xFFFFB800))
                  : null,
              onTap: () { Navigator.pop(context); onSelect(o); },
            )).toList(),
          ),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text('$label: $current',
                style: GoogleFonts.inter(
                    fontSize: 12, color: Colors.white, fontWeight: FontWeight.w500)),
            const SizedBox(width: 4),
            const Icon(Icons.expand_more_rounded, size: 16, color: Color(0xFF94A3B8)),
          ],
        ),
      ),
    );
  }

  Widget _statPill(String label, String value, Color color) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(999),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Text('$label: $value',
          style: GoogleFonts.inter(fontSize: 11, fontWeight: FontWeight.w600, color: color)),
    );
  }

  Widget _tagChip(String label, Color color) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
      decoration: BoxDecoration(
        color: color.withOpacity(0.12),
        borderRadius: BorderRadius.circular(999),
        border: Border.all(color: color.withOpacity(0.35)),
      ),
      child: Text(label,
          style: GoogleFonts.inter(fontSize: 9, fontWeight: FontWeight.w700, color: color)),
    );
  }
}
