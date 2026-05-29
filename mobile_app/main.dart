// هذا الكود يوضع داخل ملف main.dart في Flutter
Future<void> fetchResults() async {
  final response = await http.get(Uri.parse('https://your-api.onrender.com/results'));
  if (response.statusCode == 200) {
    // عرض النتائج في التطبيق
    print(json.decode(response.body));
  }
}
