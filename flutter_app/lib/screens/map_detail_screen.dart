import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../services/api_service.dart';

class MapDetailScreen extends StatefulWidget {
  final int mapId;
  const MapDetailScreen({super.key, required this.mapId});

  @override
  State<MapDetailScreen> createState() => _MapDetailScreenState();
}

class _MapDetailScreenState extends State<MapDetailScreen> {
  Map<String, dynamic>? _map;
  Map<String, dynamic>? _validationResult;
  bool _loading = true;
  bool _validating = false;
  String _newStatus = 'pending';
  final _notesCtrl = TextEditingController();
  final _actorCtrl = TextEditingController(text: 'Compliance Officer');

  @override
  void initState() {
    super.initState();
    _loadMap();
  }

  @override
  void dispose() {
    _notesCtrl.dispose();
    _actorCtrl.dispose();
    super.dispose();
  }

  Future<void> _loadMap() async {
    setState(() => _loading = true);
    final detail = await ApiService().getMapDetail(widget.mapId);
    setState(() {
      _map = detail;
      _newStatus = detail?['status'] ?? 'pending';
      _loading = false;
    });
  }

  Future<void> _runValidation() async {
    setState(() => _validating = true);
    final result = await ApiService().validateMap(widget.mapId);
    setState(() {
      _validationResult = result;
      _validating = false;
    });
  }

  Future<void> _updateStatus() async {
    final result = await ApiService().updateMapStatus(
        widget.mapId, _newStatus, _actorCtrl.text, _notesCtrl.text);
    if (result != null && mounted) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(
        content: Text('✅ MAP status updated to $_newStatus',
            style: GoogleFonts.inter(fontWeight: FontWeight.w600)),
        backgroundColor: const Color(0xFF22C55E),
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      ));
      _loadMap();
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0A1628),
      appBar: AppBar(
        title: Text('MAP Detail', style: GoogleFonts.inter(fontWeight: FontWeight.w700)),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh_rounded, color: Color(0xFFFFB800)),
            onPressed: _loadMap,
          ),
        ],
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator(color: Color(0xFFFFB800)))
          : _map == null
              ? Center(
                  child: Text('MAP not found',
                      style: GoogleFonts.inter(color: const Color(0xFF64748B))))
              : SingleChildScrollView(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      _buildMapHeader(),
                      const SizedBox(height: 16),
                      _buildUpdateSection(),
                      const SizedBox(height: 16),
                      _buildValidationSection(),
                      const SizedBox(height: 16),
                      _buildAuditLog(),
                      const SizedBox(height: 80),
                    ],
                  ),
                ),
    );
  }

  Widget _buildMapHeader() {
    final priority = _map!['priority'] ?? 'medium';
    final status = _map!['status'] ?? 'pending';
    final pColors = {
      'critical': const Color(0xFFDC2626),
      'high': const Color(0xFFEA580C),
      'medium': const Color(0xFFCA8A04),
      'low': const Color(0xFF16A34A),
    };
    final pColor = pColors[priority] ?? const Color(0xFF64748B);

    return Container(
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: const Color(0xFF0F1E35),
        borderRadius: BorderRadius.circular(16),
        border: Border(left: BorderSide(color: pColor, width: 5)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                decoration: BoxDecoration(
                  color: pColor.withOpacity(0.15),
                  borderRadius: BorderRadius.circular(999),
                  border: Border.all(color: pColor.withOpacity(0.4)),
                ),
                child: Text(priority.toUpperCase(),
                    style: GoogleFonts.inter(fontSize: 10, fontWeight: FontWeight.w700, color: pColor)),
              ),
              const SizedBox(width: 8),
              Text('#${_map!['id']}',
                  style: GoogleFonts.inter(fontSize: 11, color: const Color(0xFF475569))),
            ],
          ),
          const SizedBox(height: 10),
          Text(_map!['title'] ?? '',
              style: GoogleFonts.inter(fontSize: 17, fontWeight: FontWeight.w800, color: Colors.white)),
          const SizedBox(height: 8),
          Text(_map!['description'] ?? '',
              style: GoogleFonts.inter(fontSize: 12, color: const Color(0xFF94A3B8), height: 1.5)),
          const SizedBox(height: 14),
          Wrap(
            spacing: 8,
            runSpacing: 6,
            children: [
              _infoChip('🏢 ${_map!['department']}', const Color(0xFF2563EB)),
              _infoChip('📅 ${_map!['deadline'] ?? 'N/A'}', const Color(0xFF0891B2)),
              _infoChip(
                status == 'completed' ? '✅ Completed' : status == 'in_progress' ? '🔄 In Progress' : '⏳ ${status.replaceAll('_', ' ')}',
                status == 'completed' ? const Color(0xFF22C55E) : status == 'in_progress' ? const Color(0xFF3B82F6) : const Color(0xFF64748B),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildUpdateSection() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF0F1E35),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFF1E3A5F)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('⚙️ Update Status',
              style: GoogleFonts.inter(fontWeight: FontWeight.w700, color: Colors.white, fontSize: 15)),
          const SizedBox(height: 14),
          DropdownButtonFormField<String>(
            value: _newStatus,
            dropdownColor: const Color(0xFF0D2144),
            style: GoogleFonts.inter(color: Colors.white),
            decoration: _inputDecoration('Status'),
            items: ['pending', 'in_progress', 'completed', 'overdue', 'escalated']
                .map((s) => DropdownMenuItem(
                      value: s,
                      child: Text(s.replaceAll('_', ' ').toUpperCase(),
                          style: GoogleFonts.inter(fontSize: 13, color: Colors.white)),
                    ))
                .toList(),
            onChanged: (v) => setState(() => _newStatus = v!),
          ),
          const SizedBox(height: 10),
          TextField(
            controller: _actorCtrl,
            style: GoogleFonts.inter(color: Colors.white, fontSize: 13),
            decoration: _inputDecoration('Updated by'),
          ),
          const SizedBox(height: 10),
          TextField(
            controller: _notesCtrl,
            maxLines: 3,
            style: GoogleFonts.inter(color: Colors.white, fontSize: 13),
            decoration: _inputDecoration('Completion notes…'),
          ),
          const SizedBox(height: 14),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton.icon(
              onPressed: _updateStatus,
              icon: const Icon(Icons.save_rounded, size: 18),
              label: const Text('Save Update'),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildValidationSection() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF0F1E35),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: _validationResult != null
              ? (_validationResult!['overall_passed'] == true
                  ? const Color(0xFF22C55E)
                  : const Color(0xFFEF4444))
              : const Color(0xFF1E3A5F),
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Text('🤖 Validation Agent',
                  style: GoogleFonts.inter(fontWeight: FontWeight.w700, color: Colors.white, fontSize: 15)),
              const Spacer(),
              ElevatedButton.icon(
                onPressed: _validating ? null : _runValidation,
                icon: _validating
                    ? const SizedBox(
                        width: 14,
                        height: 14,
                        child: CircularProgressIndicator(strokeWidth: 2, color: Color(0xFF0A1628)),
                      )
                    : const Icon(Icons.play_arrow_rounded, size: 16),
                label: Text(_validating ? 'Running…' : 'Validate'),
                style: ElevatedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
                  textStyle: GoogleFonts.inter(fontSize: 12, fontWeight: FontWeight.w700),
                ),
              ),
            ],
          ),
          if (_validationResult != null) ...[
            const SizedBox(height: 14),
            _buildValidationResult(),
          ] else ...[
            const SizedBox(height: 12),
            Text('Press Validate to run automated checks on this MAP.',
                style: GoogleFonts.inter(fontSize: 12, color: const Color(0xFF64748B))),
          ],
        ],
      ),
    );
  }

  Widget _buildValidationResult() {
    final score = (_validationResult!['validation_score'] as num?)?.toDouble() ?? 0;
    final passed = _validationResult!['overall_passed'] == true;
    final checks = (_validationResult!['checks'] as List?) ?? [];
    final color = passed ? const Color(0xFF22C55E) : const Color(0xFFEF4444);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Icon(passed ? Icons.check_circle_rounded : Icons.cancel_rounded, color: color, size: 20),
            const SizedBox(width: 8),
            Text(passed ? 'PASSED' : 'FAILED',
                style: GoogleFonts.inter(fontWeight: FontWeight.w800, color: color, fontSize: 16)),
            const Spacer(),
            Text('${score.toStringAsFixed(1)}%',
                style: GoogleFonts.inter(fontWeight: FontWeight.w700, color: color, fontSize: 16)),
          ],
        ),
        const SizedBox(height: 10),
        ClipRRect(
          borderRadius: BorderRadius.circular(999),
          child: LinearProgressIndicator(
            value: score / 100,
            backgroundColor: const Color(0xFF1E3A5F),
            valueColor: AlwaysStoppedAnimation(color),
            minHeight: 8,
          ),
        ),
        const SizedBox(height: 12),
        ...checks.map<Widget>((check) {
          final ok = check['passed'] == true;
          final detail = check['detail'] ?? check['reason'] ?? '';
          return Container(
            margin: const EdgeInsets.only(bottom: 6),
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 9),
            decoration: BoxDecoration(
              color: ok ? const Color(0xFF052E1B) : const Color(0xFF2D0A0A),
              borderRadius: BorderRadius.circular(10),
              border: Border.all(
                color: ok ? const Color(0xFF22C55E).withOpacity(0.3) : const Color(0xFFDC2626).withOpacity(0.3),
              ),
            ),
            child: Row(
              children: [
                Icon(ok ? Icons.check_circle_outline_rounded : Icons.cancel_outlined,
                    color: ok ? const Color(0xFF22C55E) : const Color(0xFFDC2626), size: 16),
                const SizedBox(width: 8),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(check['check'] ?? '',
                          style: GoogleFonts.inter(
                              fontSize: 12, fontWeight: FontWeight.w600,
                              color: ok ? const Color(0xFF22C55E) : const Color(0xFFDC2626))),
                      if (detail.isNotEmpty)
                        Text(detail,
                            style: GoogleFonts.inter(fontSize: 10, color: const Color(0xFF64748B))),
                    ],
                  ),
                ),
              ],
            ),
          );
        }).toList(),
      ],
    );
  }

  Widget _buildAuditLog() {
    final logs = (_map!['audit_logs'] as List?) ?? [];
    if (logs.isEmpty) return const SizedBox.shrink();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('📋 Audit Trail',
            style: GoogleFonts.inter(fontWeight: FontWeight.w700, color: Colors.white, fontSize: 15)),
        const SizedBox(height: 10),
        ...logs.map<Widget>((log) {
          final isAgent = (log['actor'] ?? '').toString().endsWith('Agent');
          return Container(
            margin: const EdgeInsets.only(bottom: 8),
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: const Color(0xFF0F1E35),
              borderRadius: BorderRadius.circular(12),
              border: Border(
                left: BorderSide(
                  color: isAgent ? const Color(0xFFFFB800) : const Color(0xFF2563EB),
                  width: 3,
                ),
              ),
            ),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(isAgent ? '🤖' : '👤', style: const TextStyle(fontSize: 18)),
                const SizedBox(width: 10),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(log['action'] ?? '',
                          style: GoogleFonts.inter(
                              fontWeight: FontWeight.w600, color: Colors.white, fontSize: 12)),
                      const SizedBox(height: 2),
                      Text('${log['actor']} · ${(log['timestamp'] ?? '').toString().substring(0, 16)}',
                          style: GoogleFonts.inter(fontSize: 10, color: const Color(0xFF64748B))),
                      if ((log['notes'] ?? '').isNotEmpty) ...[
                        const SizedBox(height: 4),
                        Text(log['notes'],
                            style: GoogleFonts.inter(fontSize: 11, color: const Color(0xFF94A3B8))),
                      ],
                    ],
                  ),
                ),
              ],
            ),
          );
        }).toList(),
      ],
    );
  }

  InputDecoration _inputDecoration(String hint) => InputDecoration(
        hintText: hint,
        hintStyle: GoogleFonts.inter(fontSize: 13, color: const Color(0xFF475569)),
        filled: true,
        fillColor: const Color(0xFF0A1628),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(10),
          borderSide: const BorderSide(color: Color(0xFF1E3A5F)),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(10),
          borderSide: const BorderSide(color: Color(0xFF1E3A5F)),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(10),
          borderSide: const BorderSide(color: Color(0xFFFFB800)),
        ),
        contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
      );

  Widget _infoChip(String label, Color color) => Container(
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
        decoration: BoxDecoration(
          color: color.withOpacity(0.12),
          borderRadius: BorderRadius.circular(999),
          border: Border.all(color: color.withOpacity(0.35)),
        ),
        child: Text(label,
            style: GoogleFonts.inter(fontSize: 11, fontWeight: FontWeight.w600, color: color)),
      );
}
