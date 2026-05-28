import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../services/api_service.dart';

class AlertsScreen extends StatefulWidget {
  const AlertsScreen({super.key});

  @override
  State<AlertsScreen> createState() => _AlertsScreenState();
}

class _AlertsScreenState extends State<AlertsScreen> with SingleTickerProviderStateMixin {
  List<dynamic> _alerts = [];
  bool _loading = true;
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
    _loadAlerts();
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  Future<void> _loadAlerts({bool resolved = false}) async {
    setState(() => _loading = true);
    final alerts = await ApiService().getAlerts(resolved: resolved);
    setState(() {
      _alerts = alerts;
      _loading = false;
    });
  }

  Future<void> _resolve(int alertId) async {
    final result = await ApiService().resolveAlert(alertId);
    if (result != null && mounted) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(
        content: Text('✅ Alert resolved',
            style: GoogleFonts.inter(fontWeight: FontWeight.w600)),
        backgroundColor: const Color(0xFF22C55E),
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      ));
      _loadAlerts();
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0A1628),
      appBar: AppBar(
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Alerts', style: GoogleFonts.inter(fontWeight: FontWeight.w800, fontSize: 18)),
            Text('Compliance Notifications',
                style: GoogleFonts.inter(fontSize: 11, color: const Color(0xFF94A3B8))),
          ],
        ),
        bottom: TabBar(
          controller: _tabController,
          labelColor: const Color(0xFFFFB800),
          unselectedLabelColor: const Color(0xFF64748B),
          indicatorColor: const Color(0xFFFFB800),
          indicatorSize: TabBarIndicatorSize.tab,
          labelStyle: GoogleFonts.inter(fontWeight: FontWeight.w700, fontSize: 13),
          tabs: const [
            Tab(text: '🚨 Active'),
            Tab(text: '✅ Resolved'),
          ],
          onTap: (i) => _loadAlerts(resolved: i == 1),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh_rounded, color: Color(0xFFFFB800)),
            onPressed: () => _loadAlerts(resolved: _tabController.index == 1),
          ),
        ],
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          _buildAlertList(resolved: false),
          _buildAlertList(resolved: true),
        ],
      ),
    );
  }

  Widget _buildAlertList({required bool resolved}) {
    if (_loading) {
      return const Center(child: CircularProgressIndicator(color: Color(0xFFFFB800)));
    }

    if (_alerts.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(resolved ? '📭' : '✅', style: const TextStyle(fontSize: 48)),
            const SizedBox(height: 16),
            Text(
              resolved ? 'No resolved alerts yet' : 'No active alerts! All clear.',
              style: GoogleFonts.inter(color: const Color(0xFF64748B), fontSize: 15),
            ),
            if (!resolved) ...[
              const SizedBox(height: 8),
              Text('Your compliance is on track 🎉',
                  style: GoogleFonts.inter(color: const Color(0xFF22C55E), fontSize: 13)),
            ],
          ],
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: () => _loadAlerts(resolved: resolved),
      color: const Color(0xFFFFB800),
      child: ListView.separated(
        padding: const EdgeInsets.all(16),
        itemCount: _alerts.length,
        separatorBuilder: (_, __) => const SizedBox(height: 10),
        itemBuilder: (_, i) => _buildAlertCard(_alerts[i], resolved),
      ),
    );
  }

  Widget _buildAlertCard(Map alert, bool resolved) {
    final type = alert['type'] ?? '';
    final isOverdue = type.contains('overdue');
    final isCritical = type.contains('critical') || type.contains('high');

    final borderColor = isOverdue
        ? const Color(0xFFDC2626)
        : isCritical
            ? const Color(0xFFEA580C)
            : const Color(0xFFCA8A04);

    final icon = isOverdue ? '🔴' : isCritical ? '🟠' : '🟡';
    final typeLabel = type.replaceAll('_', ' ').toUpperCase();

    return Dismissible(
      key: Key('alert_${alert['id']}'),
      direction: resolved ? DismissDirection.none : DismissDirection.endToStart,
      onDismissed: (_) => _resolve(alert['id']),
      background: Container(
        alignment: Alignment.centerRight,
        padding: const EdgeInsets.only(right: 20),
        decoration: BoxDecoration(
          color: const Color(0xFF22C55E),
          borderRadius: BorderRadius.circular(14),
        ),
        child: const Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.check_circle_rounded, color: Colors.white, size: 28),
            SizedBox(height: 4),
            Text('Resolve', style: TextStyle(color: Colors.white, fontWeight: FontWeight.w700)),
          ],
        ),
      ),
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: const Color(0xFF0F1E35),
          borderRadius: BorderRadius.circular(14),
          border: Border(left: BorderSide(color: borderColor, width: 4)),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Text(icon, style: const TextStyle(fontSize: 16)),
                const SizedBox(width: 8),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                  decoration: BoxDecoration(
                    color: borderColor.withOpacity(0.12),
                    borderRadius: BorderRadius.circular(999),
                    border: Border.all(color: borderColor.withOpacity(0.4)),
                  ),
                  child: Text(typeLabel,
                      style: GoogleFonts.inter(
                          fontSize: 9, fontWeight: FontWeight.w700, color: borderColor)),
                ),
                const Spacer(),
                if (!resolved)
                  TextButton(
                    onPressed: () => _resolve(alert['id']),
                    style: TextButton.styleFrom(
                      foregroundColor: const Color(0xFF22C55E),
                      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                    ),
                    child: Text('Resolve',
                        style: GoogleFonts.inter(fontSize: 12, fontWeight: FontWeight.w700)),
                  ),
              ],
            ),
            const SizedBox(height: 10),
            Text(alert['message'] ?? '',
                style: GoogleFonts.inter(
                    fontSize: 13, fontWeight: FontWeight.w600, color: Colors.white, height: 1.4)),
            const SizedBox(height: 8),
            Row(
              children: [
                Text('MAP #${alert['map_id']}',
                    style: GoogleFonts.inter(
                        fontSize: 11, color: const Color(0xFF3B82F6), fontWeight: FontWeight.w600)),
                const SizedBox(width: 12),
                Text('📅 ${(alert['created_at'] ?? '').toString().substring(0, 10)}',
                    style: GoogleFonts.inter(fontSize: 11, color: const Color(0xFF64748B))),
                if (resolved) ...[
                  const Spacer(),
                  const Icon(Icons.check_circle_outline_rounded,
                      size: 14, color: Color(0xFF22C55E)),
                  const SizedBox(width: 4),
                  Text('Resolved',
                      style: GoogleFonts.inter(fontSize: 11, color: const Color(0xFF22C55E))),
                ],
              ],
            ),
            if (!resolved)
              Padding(
                padding: const EdgeInsets.only(top: 8),
                child: Text('← Swipe right to resolve',
                    style: GoogleFonts.inter(fontSize: 10, color: const Color(0xFF475569))),
              ),
          ],
        ),
      ),
    );
  }
}
