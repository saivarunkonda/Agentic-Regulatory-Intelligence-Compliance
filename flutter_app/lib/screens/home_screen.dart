import 'package:flutter/material.dart';
import 'dashboard_screen.dart';
import 'maps_screen.dart';
import 'departments_screen.dart';
import 'alerts_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int _currentIndex = 0;

  final List<Widget> _screens = const [
    DashboardScreen(),
    MapsScreen(),
    DepartmentsScreen(),
    AlertsScreen(),
  ];

  final List<BottomNavigationBarItem> _navItems = const [
    BottomNavigationBarItem(icon: Icon(Icons.dashboard_rounded), label: 'Dashboard'),
    BottomNavigationBarItem(icon: Icon(Icons.task_alt_rounded), label: 'MAPs'),
    BottomNavigationBarItem(icon: Icon(Icons.business_rounded), label: 'Depts'),
    BottomNavigationBarItem(icon: Icon(Icons.notifications_rounded), label: 'Alerts'),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: IndexedStack(
        index: _currentIndex,
        children: _screens,
      ),
      bottomNavigationBar: Container(
        decoration: const BoxDecoration(
          border: Border(top: BorderSide(color: Color(0xFF1E3A5F), width: 1)),
        ),
        child: BottomNavigationBar(
          currentIndex: _currentIndex,
          items: _navItems,
          onTap: (i) => setState(() => _currentIndex = i),
        ),
      ),
    );
  }
}
