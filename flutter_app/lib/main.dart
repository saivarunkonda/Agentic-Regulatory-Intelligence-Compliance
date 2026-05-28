import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'screens/splash_screen.dart';

void main() {
  runApp(const SuRakshaApp());
}

class SuRakshaApp extends StatelessWidget {
  const SuRakshaApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'SuRaksha – Regulatory Intelligence',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        useMaterial3: true,
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF0A1628),
          brightness: Brightness.dark,
          primary: const Color(0xFFFFB800),
          secondary: const Color(0xFF1E40AF),
          surface: const Color(0xFF0F1E35),
          background: const Color(0xFF0A1628),
        ),
        scaffoldBackgroundColor: const Color(0xFF0A1628),
        textTheme: GoogleFonts.interTextTheme(ThemeData.dark().textTheme),
        appBarTheme: AppBarTheme(
          backgroundColor: const Color(0xFF0D2144),
          foregroundColor: Colors.white,
          elevation: 0,
          centerTitle: false,
          titleTextStyle: GoogleFonts.inter(
            color: Colors.white,
            fontWeight: FontWeight.w700,
            fontSize: 18,
          ),
        ),
        cardTheme: CardThemeData(
          color: const Color(0xFF0F1E35),
          elevation: 0,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
            side: const BorderSide(color: Color(0xFF1E3A5F), width: 1),
          ),
        ),
        elevatedButtonTheme: ElevatedButtonThemeData(
          style: ElevatedButton.styleFrom(
            backgroundColor: const Color(0xFFFFB800),
            foregroundColor: const Color(0xFF0A1628),
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            textStyle: GoogleFonts.inter(fontWeight: FontWeight.w700),
            padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
          ),
        ),
        chipTheme: ChipThemeData(
          backgroundColor: const Color(0xFF1E3A5F),
          labelStyle: GoogleFonts.inter(fontSize: 11, fontWeight: FontWeight.w600),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(999)),
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
        ),
        bottomNavigationBarTheme: const BottomNavigationBarThemeData(
          backgroundColor: Color(0xFF0D2144),
          selectedItemColor: Color(0xFFFFB800),
          unselectedItemColor: Color(0xFF64748B),
          type: BottomNavigationBarType.fixed,
          elevation: 0,
        ),
      ),
      home: const SplashScreen(),
    );
  }
}
