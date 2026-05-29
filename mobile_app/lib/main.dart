import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

void main() => runApp(const MikroTikScannerApp());

class MikroTikScannerApp extends StatelessWidget {
  const MikroTikScannerApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'ماسح ميكروتيك الذكي',
      theme: ThemeData(primarySwatch: Colors.indigo),
      home: const ScanDashboard(),
    );
  }
}

class ScanDashboard extends StatefulWidget {
  const ScanDashboard({Key? key}) : super(key: key);

  @override
  State<ScanDashboard> createState() => _ScanDashboardState();
}

class _ScanDashboardState extends State<ScanDashboard> {
  final _ipController = TextEditingController(text: '192.168.88.1');
  final _apiController = TextEditingController(text: 'https://your-secured-cloud-api.onrender.com');
  bool _isLoading = false;
  Map<String, dynamic>? _results;
  String _statusMessage = 'أدخل عنوان الـ IP ورابط الـ API لبدء الفحص';

  Future<void> triggerVulnerabilityScan() async {
    setState(() {
      _isLoading = true;
      _statusMessage = 'جاري إجراء فحص المنافذ والتكوين بميكروتيك...';
      _results = null;
    });

    final apiBaseUrl = _apiController.text.trim();
    final apiUrl = Uri.parse('$apiBaseUrl/scan');
    
    try {
      final response = await http.post(
        apiUrl,
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'ip': _ipController.text,
          'port': 8291,
          'username': 'admin',
          'password': '',
          'check_default_credentials': true
        }),
      );

      if (response.statusCode == 202) {
        final jobData = json.decode(response.body);
        final scanId = jobData['scan_id'];
        _statusMessage = 'تم تسجيل الفحص وعرّف العملية: $scanId';
        
        // محاكاة استجواب ومسح النتائج (/results/{id}) بعد قليل من الوقت
        await Future.delayed(const Duration(seconds: 3));
        await fetchScanResults(scanId);
      } else {
        setState(() {
          _statusMessage = 'فشل الاتصال بالسيرفر المركزي لـ API: ${response.statusCode}';
        });
      }
    } catch (e) {
      setState(() {
        _statusMessage = 'حدث خطأ غير متوقع أثناء استكشاف الشبكة: $e';
      });
    } finally {
      setState(() { _isLoading = false; });
    }
  }

  Future<void> fetchScanResults(String scanId) async {
    final apiBaseUrl = _apiController.text.trim();
    final resultsUrl = Uri.parse('$apiBaseUrl/results/$scanId');
    try {
      final response = await http.get(resultsUrl);
      if (response.statusCode == 200) {
        setState(() {
          _results = json.decode(response.body);
          _statusMessage = "اكتمل الفحص بنجاح!";
        });
      }
    } catch (e) {
      print("خطأ جلب النتائج: $e");
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('لوحة تحكم الفحص ومكافحة الاختراق')),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            TextField(
              controller: _apiController,
              decoration: const InputDecoration(
                labelText: 'رابط خادم الـ API (FastAPI Backend URL)',
                hintText: 'https://your-secured-cloud-api.onrender.com',
                prefixIcon: Icon(Icons.link),
              ),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: _ipController,
              decoration: const InputDecoration(
                labelText: 'عنوان IP لجهاز MikroTik',
                prefixIcon: Icon(Icons.router),
              ),
            ),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: _isLoading ? null : triggerVulnerabilityScan,
              child: _isLoading 
                ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator())
                : const Text('بدء فحص الثغرات الحية'),
            ),
            const SizedBox(height: 24),
            Text(_statusMessage, style: const TextStyle(fontWeight: FontWeight.bold)),
            if (_results != null) ...[
              const Divider(),
              Expanded(
                child: ListView(
                  children: [
                    Text('الهدف الممسوح: ${_results!["results"]?["ip_address"] ?? ""}'),
                    Text('معدّل الأمان بالراوتر: ${_results!["results"]?["security_score"] ?? ""}%'),
                    Text('إصدار الـ OS: ${_results!["results"]?["routeros_version"] ?? ""}'),
                    Text('حساب admin بدون كلمة مرور: ${_results!["results"]?["default_credentials_vulnerable"] ?? ""}')
                  ],
                ),
              )
            ]
          ],
        ),
      ),
    );
  }
}
