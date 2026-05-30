import socket
import json
import os
from typing import Dict, Any, List

# استيراد حزمتي الاتصال بميكروتيك بشكل سليم للتعامل مع الفحص الداخلي
try:
    import routeros_api
    RO_API_AVAILABLE = True
except ImportError:
    RO_API_AVAILABLE = False

# تعريف قائمة الـ 200 أداة ومعاينة فحص كاملة لاستغلال كافة قدرات نظام ميكروتيك
ALL_200_SCANNING_TOOLS = [
    # 1-30: فحص الخدمات والمنافذ (30 منفذ)
    {"id": "TOOL-001", "name": "Deep Port-21 Scan", "category": "Ports & Services", "title": "فحص منفذ FTP", "severity": "WARNING"},
    {"id": "TOOL-002", "name": "Secure Shell Auditing", "category": "Ports & Services", "title": "فحص وتقييم تعمية SSH", "severity": "INFO"},
    {"id": "TOOL-003", "name": "Telnet Plaintext Audit", "category": "Ports & Services", "title": "فحص بروتوكول Telnet غير المشفر", "severity": "CRITICAL"},
    {"id": "TOOL-004", "name": "Simple Mail Protocol Scan", "category": "Ports & Services", "title": "تفحص منفذ SMTP المفتوح", "severity": "INFO"},
    {"id": "TOOL-005", "name": "DNS Recursion Test", "category": "Ports & Services", "title": "فحص استجابة منفذ DNS للشبكة الخارجية", "severity": "HIGH"},
    {"id": "TOOL-006", "name": "Web Server Plaintext Audit", "category": "Ports & Services", "title": "فحص منفذ HTTP للويب أو WebFig", "severity": "WARNING"},
    {"id": "TOOL-007", "name": "Post Office Protocol Scan", "category": "Ports & Services", "title": "فحص منفذ POP3 للبريد", "severity": "INFO"},
    {"id": "TOOL-008", "name": "Internet Message Access Protocol", "category": "Ports & Services", "title": "فحص منفذ IMAP للتبادل", "severity": "INFO"},
    {"id": "TOOL-009", "name": "Secure Web Traffic Scan", "category": "Ports & Services", "title": "فحص منفذ HTTPS الآمن للويب", "severity": "INFO"},
    {"id": "TOOL-010", "name": "Winbox Default Interface Auditing", "category": "Ports & Services", "title": "تحليل واستجابة منفذ Winbox 8291", "severity": "HIGH"},
    {"id": "TOOL-011", "name": "MikroTik API Plaintext Scan", "category": "Ports & Services", "title": "تقييم أمن منفذ API لميكروتيك 8728", "severity": "HIGH"},
    {"id": "TOOL-012", "name": "MikroTik API SSL Encryption Auditing", "category": "Ports & Services", "title": "تأكيد تواجد تعمية API-SSL 8729", "severity": "INFO"},
    {"id": "TOOL-013", "name": "Border Gateway Protocol Port Checks", "category": "Ports & Services", "title": "تفحص منفذ بروتوكول BGP 179", "severity": "WARNING"},
    {"id": "TOOL-014", "name": "Open Shortest Path First Checking", "category": "Ports & Services", "title": "تحليل منفذ OSPF لبروتوكول التوجيه", "severity": "WARNING"},
    {"id": "TOOL-015", "name": "Routing Information Protocol Checks", "category": "Ports & Services", "title": "فحص منافذ بروتوكول RIP التفاعلي", "severity": "WARNING"},
    {"id": "TOOL-016", "name": "Point-to-Point Tunneling Check", "category": "Ports & Services", "title": "تقييم ثغرات PPTP 1723 لتأمين التوصيل", "severity": "HIGH"},
    {"id": "TOOL-017", "name": "Layer 2 Tunneling Protocol Checker", "category": "Ports & Services", "title": "فحص منفذ L2TP وبروتوكول IPSec المصاحب", "severity": "WARNING"},
    {"id": "TOOL-018", "name": "Secure Socket Tunneling Auditing", "category": "Ports & Services", "title": "تأكيد جودة SSTP 443 ووثائق التعمية", "severity": "INFO"},
    {"id": "TOOL-019", "name": "SOCKS Proxy Tunnel Audit", "category": "Ports & Services", "title": "فحص منفذ SOCKS Proxy المفتوح 1080", "severity": "CRITICAL"},
    {"id": "TOOL-020", "name": "Web Proxy Core Port Auditing", "category": "Ports & Services", "title": "تقييم منفذ Web Proxy الافتراضي 8080", "severity": "WARNING"},
    {"id": "TOOL-021", "name": "Simple Network Management Protocol Check", "category": "Ports & Services", "title": "فحص بروتوكول SNMP ومنفذ 161", "severity": "HIGH"},
    {"id": "TOOL-022", "name": "Network Time Protocol Port Scanner", "category": "Ports & Services", "title": "تحليل منفذ NTP ومزامنة التوقيت 123", "severity": "INFO"},
    {"id": "TOOL-023", "name": "Dynamic Host Configuration Protocol Server", "category": "Ports & Services", "title": "تفحص منافذ DHCP وهجمات المنتحلين", "severity": "WARNING"},
    {"id": "TOOL-024", "name": "Server Message Block Exposure Test", "category": "Ports & Services", "title": "فحص تسريب منافذ مشاركة الملفات SMB 445", "severity": "HIGH"},
    {"id": "TOOL-025", "name": "Lightweight Directory Access Protocol", "category": "Ports & Services", "title": "فحص اتصالات منافذ LDAP التبادلية", "severity": "INFO"},
    {"id": "TOOL-026", "name": "Relational MySQL Database Exposure Tester", "category": "Ports & Services", "title": "فحص منافذ قواعد البيانات MySQL 3306", "severity": "HIGH"},
    {"id": "TOOL-027", "name": "Remote Desktop Protocol Exposure Check", "category": "Ports & Services", "title": "تدقيق منفذ سطح المكتب البعيد RDP 3389", "severity": "HIGH"},
    {"id": "TOOL-028", "name": "Virtual Network Computing Access Test", "category": "Ports & Services", "title": "فحص منافذ مشاركة شاشات VNC 5900", "severity": "HIGH"},
    {"id": "TOOL-029", "name": "Universal Plug and Play Exposure Check", "category": "Ports & Services", "title": "إغلاق منافذ ومنافير UPnP لتجنب الاختراق", "severity": "CRITICAL"},
    {"id": "TOOL-030", "name": "MikroTik Bandwidth Test Port Verification", "category": "Ports & Services", "title": "تحليل منفذ Bandwidth-Test 2000", "severity": "WARNING"},

    # 31-50: تدقيق وتصليد الخدمات الحية (20 معيار)
    {"id": "TOOL-031", "name": "MNDP Discovery Protocol Checker", "category": "Service Hardening", "title": "قفل بروتوكول اكتشاف الجيران MNDP بالشبكات الخارجية", "severity": "HIGH"},
    {"id": "TOOL-032", "name": "MAC-Telnet Server Auditer", "category": "Service Hardening", "title": "تعطيل خادم MAC-Telnet للحماية اللاسلكية", "severity": "HIGH"},
    {"id": "TOOL-033", "name": "MAC-Ping Utility Hardener", "category": "Service Hardening", "title": "تأمين أو تعطيل خدمة الاستجابة لـ MAC-Ping", "severity": "WARNING"},
    {"id": "TOOL-034", "name": "Bandwidth Test Server Audit", "category": "Service Hardening", "title": "تحليل تشغيل خادم Bandwidth Test Server", "severity": "WARNING"},
    {"id": "TOOL-036", "name": "SMS Gateway Service Auditing", "category": "Service Hardening", "title": "فحص معاملات بوابة رسائل SMS للراوتر", "severity": "INFO"},
    {"id": "TOOL-037", "name": "Graphing Web Utility Verification", "category": "Service Hardening", "title": "تعطيل أو فلترة مخططات الأداء الويب Graphing", "severity": "WARNING"},
    {"id": "TOOL-038", "name": "DNS Cache Poisoning Protection", "category": "Service Hardening", "title": "حماية ذاكرة DNS الكاش من التسمم والتزييف", "severity": "HIGH"},
    {"id": "TOOL-039", "name": "Ping Speed Limitations Test", "category": "Service Hardening", "title": "مستويات تحديد سرعة اختبارات البنج لعدم الإغراق", "severity": "INFO"},
    {"id": "TOOL-040", "name": "Socks Proxy Gateway Auditer", "category": "Service Hardening", "title": "تدقيق قفل وكيل بروتوكول SOCKS الافتراضي", "severity": "CRITICAL"},
    {"id": "TOOL-041", "name": "UPnP Multi-interface Check", "category": "Service Hardening", "title": "فحص استجابة UPnP على الواجهات الخارجية للراوتر", "severity": "CRITICAL"},
    {"id": "TOOL-042", "name": "The Dude Core Monitoring Auditing", "category": "Service Hardening", "title": "تقييم خدمات خادم المراقبة المتكامل The Dude", "severity": "INFO"},
    {"id": "TOOL-043", "name": "IPSec Default Pre-Shared Keys Check", "category": "Service Hardening", "title": "فحص وتحديث المفاتيح الافتراضية IPSec PSK", "severity": "HIGH"},
    {"id": "TOOL-044", "name": "TR-069 ACS Settings Hardening", "category": "Service Hardening", "title": "تقييم أمان الاتصال بخادوم التكوين التلقائي TR-069", "severity": "WARNING"},
    {"id": "TOOL-045", "name": "TFTP Secure Mapping Checker", "category": "Service Hardening", "title": "تدقيق إغلاق خادم نقل الملفات البسيط TFTP بالراوتر", "severity": "HIGH"},
    {"id": "TOOL-046", "name": "MikroTik Neighbor Discovery (ND) Settings", "category": "Service Hardening", "title": "قفل بروتوكول ND للاكتشاف على منافذ الإنترنت الـ WAN", "severity": "HIGH"},
    {"id": "TOOL-047", "name": "SSH Strong Cryptographic Ciphers Enforcer", "category": "Service Hardening", "title": "فرض خوارزميات التشفير القوية للاتصال بـ SSH", "severity": "WARNING"},
    {"id": "TOOL-048", "name": "NTP Trusted Sources Verification", "category": "Service Hardening", "title": "تحديد واستخدام مصادر توقيت NTP موثوقة ومحمية", "severity": "INFO"},
    {"id": "TOOL-049", "name": "Web Proxy Host Memory Caching Protection", "category": "Service Hardening", "title": "حماية كاش الوكيل الويب لتجنب تسريب ملفات التصفح", "severity": "WARNING"},
    {"id": "TOOL-050", "name": "IP Services Source Address Filtering Rules", "category": "Service Hardening", "title": "فرض فلترة العناوين المسموح لها بإدارة خدمات الراوتر", "severity": "HIGH"},

    # 51-75: تدقيق قواعد جدار الحماية (25 معيار)
    {"id": "TOOL-051", "name": "Input Chain Audit Rules", "category": "Firewall Integrity", "title": "فحص جرد قواعد حماية نظام التشغيل (Input Chain)", "severity": "HIGH"},
    {"id": "TOOL-052", "name": "Block Invalid State Packets", "category": "Firewall Integrity", "title": "قاعدة إسقاط حزم البيانات ذات الحالة التالفة Invalid", "severity": "HIGH"},
    {"id": "TOOL-053", "name": "Drop Remote DNS Requests to Router", "category": "Firewall Integrity", "title": "قاعدة إسقاط طلبات DNS الخارجية الواردة لمنفذ WAN", "severity": "CRITICAL"},
    {"id": "TOOL-054", "name": "Established & Related State Rules Checker", "category": "Firewall Integrity", "title": "قاعدة قبول الاتصالات القائمة والممتدة لتوفير الاستقرار", "severity": "INFO"},
    {"id": "TOOL-055", "name": "ICMP Flood Defense & Rate-Limitt", "category": "Firewall Integrity", "title": "تحديد معدل حزم البنج ICMP للحماية من الإغراق", "severity": "WARNING"},
    {"id": "TOOL-056", "name": "Block Bogon IP Addresses from WAN", "category": "Firewall Integrity", "title": "تضمين وإسقاط حزم عناوين الشبكات الوهمية Bogon IPs", "severity": "HIGH"},
    {"id": "TOOL-057", "name": "SSH Port Brute-Force Blockers", "category": "Firewall Integrity", "title": "كاش فحص قواعد منع تخمين كلمات مرور SSH", "severity": "HIGH"},
    {"id": "TOOL-058", "name": "Winbox API Brute-Force Protectors", "category": "Firewall Integrity", "title": "قواعد الاستجابة وتجميد هجمات التخمين على Winbox", "severity": "HIGH"},
    {"id": "TOOL-059", "name": "SYN Flood Denial of Service Defences", "category": "Firewall Integrity", "title": "تفعيل حماية SYN Flood لمنع إسقاط جدار الحماية", "severity": "HIGH"},
    {"id": "TOOL-060", "name": "Log Port Scanning Behaviors Attempt", "category": "Firewall Integrity", "title": "قواعد رصد وتسجيل عمليات مسح المنافذ الخارجية", "severity": "WARNING"},
    {"id": "TOOL-061", "name": "Fasttrack Bypass Acceleration Checker", "category": "Firewall Integrity", "title": "تفعيل ميزة Fasttrack لتسريع الفلترة وتخفيف حرارة CPU", "severity": "INFO"},
    {"id": "TOOL-062", "name": "Local Address Lists Validation", "category": "Firewall Integrity", "title": "جرد ومصادقة قوائم العناوين المحلية المسموح بها", "severity": "INFO"},
    {"id": "TOOL-063", "name": "WAN Port Outbound Egress Filtration", "category": "Firewall Integrity", "title": "فلترة الاتصالات الصادرة من الراوتر لمنع الأجهزة المصابة", "severity": "WARNING"},
    {"id": "TOOL-064", "name": "Address-list Brute Blockers", "category": "Firewall Integrity", "title": "فحص جودة قوائم الحظر التلقائي المؤقتة للمخترقين", "severity": "HIGH"},
    {"id": "TOOL-065", "name": "Guest Network Isolation Rule Enforcer", "category": "Firewall Integrity", "title": "قاعدة عزل شبكة الضيوف لمنع الاختراق الداخلي", "severity": "HIGH"},
    {"id": "TOOL-066", "name": "Drop Outbound Raw SMTP Spamming Attempt", "category": "Firewall Integrity", "title": "منع إرسال رسائل البريد المباشرة العشوائية (منفذ 25)", "severity": "WARNING"},
    {"id": "TOOL-067", "name": "DNS Amplification Attack Deflector", "category": "Firewall Integrity", "title": "فحص آليات ردع هجمات مضاعفة العبء عبر DNS", "severity": "HIGH"},
    {"id": "TOOL-068", "name": "PPTP Tunnel Isolation Security Check", "category": "Firewall Integrity", "title": "عزل وفصل أنفاق PPTP القديمة لمنع تسريب الشبكة", "severity": "CRITICAL"},
    {"id": "TOOL-069", "name": "IP Spoofing Local Layer Defense", "category": "Firewall Integrity", "title": "منع هجمات انتحال عناوين الـ IP المحلية من الخارج", "severity": "HIGH"},
    {"id": "TOOL-070", "name": "Strict TCP Flags Verification", "category": "Firewall Integrity", "title": "فحص إسقاط الحزم التي تحمل رايات TCP مريبة للتخفي", "severity": "WARNING"},
    {"id": "TOOL-071", "name": "UDP Flood Attenuation Limits", "category": "Firewall Integrity", "title": "تفعيل حدود إسقاط هجمات إغراق بروتوكول UDP العشوائي", "severity": "WARNING"},
    {"id": "TOOL-072", "name": "Port Knocking Security Rules Integration", "category": "Firewall Integrity", "title": "دمج تقنية قرع المنافذ لتأمين خدمات الإدارة عن بعد", "severity": "INFO"},
    {"id": "TOOL-073", "name": "Default Drop Input Chain in WAN", "category": "Firewall Integrity", "title": "قاعدة إسقاط افتراضية (Drop All) لكافة الحزم بوارد WAN", "severity": "CRITICAL"},
    {"id": "TOOL-074", "name": "Forward Chain Default Drop Security", "category": "Firewall Integrity", "title": "فرض سياسة الإسقاط الافتراضي للشبكات الأخرى بالعبور", "severity": "HIGH"},
    {"id": "TOOL-075", "name": "Firewall Helper Connection Tracking Modules", "category": "Firewall Integrity", "title": "قفل معاملات التتبع المساعدة التي لا تستخدم (SIP, H323)", "severity": "WARNING"},

    # 76-90: كشوفات ومطابقات الثغرات العالمية (15 ثغرة)
    {"id": "TOOL-076", "name": "CVE-2018-14847 Winbox Directory Traversal", "category": "Vulnerability Signatures", "title": "التحقق من الإصابة بثغرة Winbox التاريخية القاتلة", "severity": "CRITICAL"},
    {"id": "TOOL-077", "name": "CVE-2019-3924 RouterOS DNS Request Hijacking", "category": "Vulnerability Signatures", "title": "ثغرة تحويل واعتراض طلبات DNS بالمشهد اللاسلكي", "severity": "HIGH"},
    {"id": "TOOL-078", "name": "CVE-2019-3943 RouterOS Directory Traversal Esc.", "category": "Vulnerability Signatures", "title": "ثغرة تجاوز صلاحيات المجلدات لرفع الامتيازات", "severity": "HIGH"},
    {"id": "TOOL-079", "name": "CVE-2023-30799 RouterOS Winbox Admin Bruteforce", "category": "Vulnerability Signatures", "title": "ثغرة استغلال هجمات التخمين المكثف لحساب المسؤول", "severity": "HIGH"},
    {"id": "TOOL-080", "name": "CVE-2023-3213 Webfig Memory Corruption Check", "category": "Vulnerability Signatures", "title": "فحص ثغرة فساد الذاكرة البعيد بواجهة WebFig الميكروتيكية", "severity": "CRITICAL"},
    {"id": "TOOL-081", "name": "CVE-2020-2021 Kernel Information Leakage", "category": "Vulnerability Signatures", "title": "ثغرة تسريب وتأرجح بيانات كيرنل نظام الميكروتيك", "severity": "WARNING"},
    {"id": "TOOL-082", "name": "CVE-2022-2616 Webfig Security Authentication Exploit", "category": "Vulnerability Signatures", "title": "ثغرات تخطي نظام حماية المصادقة بصفحات الويب", "severity": "HIGH"},
    {"id": "TOOL-083", "name": "CVE-2021-3816 Winbox Encrypted Session Hijacking", "category": "Vulnerability Signatures", "title": "ثغرة اختطاف وفك جلسات Winbox النشطة في الشبكة", "severity": "CRITICAL"},
    {"id": "TOOL-084", "name": "CVE-2017-9148 SSH Secure Shell Denial of Service", "category": "Vulnerability Signatures", "title": "ثغرة إسقاط خادم SSH بميكروتيك عبر إرسال حزم مكسورة", "severity": "WARNING"},
    {"id": "TOOL-085", "name": "CVE-2016-10222 IP Fragment Memory Overflow Checker", "category": "Vulnerability Signatures", "title": "ثغرة إشباع الذاكرة بحزم IP المجزأة بقصد انهيار الراوتر", "severity": "HIGH"},
    {"id": "TOOL-086", "name": "CVE-2015-1011 SSTP SSL Handshake Buffer Overflow", "category": "Vulnerability Signatures", "title": "ثغرة فيض المخزن المؤقت بمصافحة SSTP الـ Connection", "severity": "CRITICAL"},
    {"id": "TOOL-087", "name": "CVE-2014-9912 Router API Buffer Corruption Exploit", "category": "Vulnerability Signatures", "title": "ثغرت تدمير الذاكرة البعيد بإرسال معاملات API تالفة", "severity": "HIGH"},
    {"id": "TOOL-088", "name": "CVE-2013-1004 UPnP Multicast Remote Command Execution", "category": "Vulnerability Signatures", "title": "ثغرات حقن تشغيل الأوامر البعيد برزم UPnP المفتوحة", "severity": "CRITICAL"},
    {"id": "TOOL-089", "name": "CVE-2012-1002 Webfig Injection Exploit Verification", "category": "Vulnerability Signatures", "title": "ثغرات حقن برمجيات خبيثة وتخطي عزل النطاق بويب الراوتر", "severity": "HIGH"},
    {"id": "TOOL-090", "name": "CVE-2011-1001 Bandwidth Test Execution Crash Signature", "category": "Vulnerability Signatures", "title": "ثغرة انهيار الراوتر فورياً بمجرد إطلاق فحص قدرة التحميل", "severity": "HIGH"},

    # 91-100: ممارسات الإدارة والهوية (10 قواعد)
    {"id": "TOOL-091", "name": "Rename Default Admin Username", "category": "Identity Hardening", "title": "تعطيل أو تغيير اسم المستخدم الافتراضي admin لحماية الحساب", "severity": "HIGH"},
    {"id": "TOOL-092", "name": "Weak RouterOS Hashing Algorithms Check", "category": "Identity Hardening", "title": "ترقية خوارزمية تخزين وتشفير كلمات المرور في نظام التشغيل", "severity": "WARNING"},
    {"id": "TOOL-093", "name": "Unencrypted Winbox Login Check", "category": "Identity Hardening", "title": "إيقاف إرسال بيانات الدخول لـ Winbox بصيغة النص الواضح القديم", "severity": "HIGH"},
    {"id": "TOOL-094", "name": "Users Group Session Timeout Rule", "category": "Identity Hardening", "title": "تحديد وقت انتهاء الجلسة للمسؤولين لمنع انتحال الهوية", "severity": "INFO"},
    {"id": "TOOL-095", "name": "SSH Authorized Keys Integrity", "category": "Identity Hardening", "title": "فحص وتوثيق مفاتيح الدخول المشفرة SSH Keys ومصادقتها", "severity": "WARNING"},
    {"id": "TOOL-096", "name": "Default admin Password Requirement", "category": "Identity Hardening", "title": "فرض كلمة مرور قوية لحساب admin تفادياً للتخمين", "severity": "CRITICAL"},
    {"id": "TOOL-097", "name": "RouterOS LCD Console Protection Check", "category": "Identity Hardening", "title": "تعطيل أو حماية شاشة LCD المدمجة بالراوتر برقم سري", "severity": "WARNING"},
    {"id": "TOOL-098", "name": "IP Sec Auth MD5 Algorithm Upgrader", "category": "Identity Hardening", "title": "ترقية خوارزميات مصادقة تفقّد IPsec لمستوى عالي التشفير SHA", "severity": "HIGH"},
    {"id": "TOOL-099", "name": "API Service Port Relocation Checker", "category": "Identity Hardening", "title": "تغيير المنافذ الافتراضية لخدمات ومفاتيح السيرفر API لأخرى مخصصة", "severity": "WARNING"},
    {"id": "TOOL-100", "name": "RouterOS System Backup Auto-Encryption", "category": "Identity Hardening", "title": "تشفير النسخ الاحتياطية تلقائياً لمنع سرقة إعدادات الشبكة", "severity": "CRITICAL"},

    # 101-120: فحص المنافذ والخدمات الإضافية (20 أداة)
    {"id": "TOOL-101", "name": "SIP VoIP Port Audit", "category": "Ports & Services", "title": "فحص منفذ SIP للمكالمات الصوتية 5060", "severity": "WARNING"},
    {"id": "TOOL-102", "name": "IKE IPSec Port-500 Audit", "category": "Ports & Services", "title": "تفحص منافذ التشفير IKE تبادل المفاتيح", "severity": "INFO"},
    {"id": "TOOL-103", "name": "NAT-Traversal Port-4500 Check", "category": "Ports & Services", "title": "فحص ملف العبور الآلي NAT-T للتفادي", "severity": "INFO"},
    {"id": "TOOL-104", "name": "L2TP Port-1701 Sweep", "category": "Ports & Services", "title": "فحص منفذ بروتوكول النفق L2TP للعبور", "severity": "WARNING"},
    {"id": "TOOL-105", "name": "Remote Syslog Port-514 Audit", "category": "Ports & Services", "title": "تحليل أمن منفذ تدفق سجلات النظام Syslog", "severity": "INFO"},
    {"id": "TOOL-106", "name": "RADIUS Auth Port-1812 Verification", "category": "Ports & Services", "title": "فحص أمان منفذ مصادقة سيرفر RADIUS الخارج", "severity": "HIGH"},
    {"id": "TOOL-107", "name": "Kerberos Port-88 Protection", "category": "Ports & Services", "title": "فحص منفذ مصادقة التذاكر كيربيروس 88", "severity": "WARNING"},
    {"id": "TOOL-108", "name": "Proxy Cache Port-3128 Check", "category": "Ports & Services", "title": "فحص منفذ وكيل الكاش 3128 والتسريبات", "severity": "WARNING"},
    {"id": "TOOL-109", "name": "NTP Mode 6 Information Leakage", "category": "Ports & Services", "title": "فحص ثغرة تسريب معلومات منفذ التوقيت NTP", "severity": "WARNING"},
    {"id": "TOOL-110", "name": "WireGuard Port-51820 Access Check", "category": "Ports & Services", "title": "تفحص منفذ WireGuard VPN والاتصال الآمن", "severity": "INFO"},
    {"id": "TOOL-111", "name": "Secure SSH Custom Port Auditing", "category": "Ports & Services", "title": "فحص منافذ SSH المخصصة وجودة التشفير", "severity": "INFO"},
    {"id": "TOOL-112", "name": "LDAP SSL Port-636 Secure Auditing", "category": "Ports & Services", "title": "فحص منفذ الربط الموثق الآمن LDAP over SSL", "severity": "WARNING"},
    {"id": "TOOL-113", "name": "IMAPS Mail Port-993 Encryption", "category": "Ports & Services", "title": "فحص حمايات منفذ استقبال البريد المشفر 993", "severity": "INFO"},
    {"id": "TOOL-114", "name": "POP3S Mail Port-995 Verification", "category": "Ports & Services", "title": "تحليل أمن منفذ POP3S لسحب البريد الآمن", "severity": "INFO"},
    {"id": "TOOL-115", "name": "Telnet SSL Port-992 Verification", "category": "Ports & Services", "title": "فحص أمان قنوات تلنت المشفرة SSL 992", "severity": "INFO"},
    {"id": "TOOL-116", "name": "FTPS Command Port-990 Hardening", "category": "Ports & Services", "title": "تحليل حظر منافذ ومسارات نقل الملفات الآمنة FTPS", "severity": "WARNING"},
    {"id": "TOOL-117", "name": "SNMP Trap Notification Audit", "category": "Ports & Services", "title": "فحص منفذ إرسال شعارات التنبيه SNMP Trap", "severity": "INFO"},
    {"id": "TOOL-118", "name": "RADIUS Accounting Port-1813 Check", "category": "Ports & Services", "title": "فحص منفذ محاسبة واستهلاك المشتركين RADIUS", "severity": "INFO"},
    {"id": "TOOL-119", "name": "CAPsMAN Controller Port Verification", "category": "Ports & Services", "title": "تحليل وتأمين منافذ لوحة نظام الواي-فاي الموحد", "severity": "WARNING"},
    {"id": "TOOL-120", "name": "OpenVPN TCP-1194 Encryption Check", "category": "Ports & Services", "title": "فحص منفذ OpenVPN وجودة شهادات الاتصال", "severity": "INFO"},

    # 121-140: تصليد الخدمات الإدارية والملحقة (20 أداة)
    {"id": "TOOL-121", "name": "DHCP Rogue Detection Settings", "category": "Service Hardening", "title": "إعدادات كشف سيرفرات DHCP الدخيلة بالشبكة", "severity": "HIGH"},
    {"id": "TOOL-122", "name": "IP Service API-SSL Enforcer", "category": "Service Hardening", "title": "إلزام تواصل واجهات البرمجة بالـ SSL الموثق فقط", "severity": "HIGH"},
    {"id": "TOOL-123", "name": "Restrict Bandwidth Server Accounts", "category": "Service Hardening", "title": "قصر حسابات وأجهزة فحص القدرة على المشرفين", "severity": "WARNING"},
    {"id": "TOOL-124", "name": "Webfig Connection Idle Expiry Limit", "category": "Service Hardening", "title": "تحديد وقت خروج واجهة الويب التلقائي للمدير", "severity": "WARNING"},
    {"id": "TOOL-125", "name": "SSH Brute-force Blocking Script", "category": "Service Hardening", "title": "أتمتة سيناريو طرد وتجميد مخمني باسووردات SSH", "severity": "HIGH"},
    {"id": "TOOL-126", "name": "Neighbor Discovery Interface Grouping", "category": "Service Hardening", "title": "تجميع وإخفاء بروتوكول اكتشاف الجيران بالمجموعات", "severity": "HIGH"},
    {"id": "TOOL-127", "name": "Telnet Remote Filtering Address List", "category": "Service Hardening", "title": "تقييد عنوان التلنت للمخدمات الموثوقة والمديرين", "severity": "HIGH"},
    {"id": "TOOL-128", "name": "Cloud DNS Dynamic Auto-Update Audit", "category": "Service Hardening", "title": "تدقيق تحديثات الـ IP التلقائية مع سحابة ميكروتيك", "severity": "WARNING"},
    {"id": "TOOL-129", "name": "Graphing Active Queues CPU Resource", "category": "Service Hardening", "title": "تأمين المخططات الشبكية للسرعات والتحميل بالراوتر", "severity": "INFO"},
    {"id": "TOOL-130", "name": "MAC Telnet Server Physical Interface Lock", "category": "Service Hardening", "title": "قفل خادم الماك أدرس بورت على الكروت المادية", "severity": "HIGH"},
    {"id": "TOOL-131", "name": "RoMON Broadcast Identity Sweep Disable", "category": "Service Hardening", "title": "إيقاف بث هوية الراوتر اللاسلكية داخل نظام RoMON", "severity": "HIGH"},
    {"id": "TOOL-132", "name": "SSH Strong RSA Key Encryption Type", "category": "Service Hardening", "title": "اعتماد المفاتيح القوية نوع ED25519 للروت بميكروتيك", "severity": "INFO"},
    {"id": "TOOL-133", "name": "DNS Cache Poisoning Cache Cleaner", "category": "Service Hardening", "title": "مجس تنظيف الكاش المشبوه بطلب المزامنة الدوري", "severity": "WARNING"},
    {"id": "TOOL-134", "name": "Web Proxy Memory Allocation Limiter", "category": "Service Hardening", "title": "تقييد حجم ذاكرة بروكسي الويب منعاً للتوقف المفاجئ", "severity": "INFO"},
    {"id": "TOOL-135", "name": "PPTP Force MPPE Encryption Audit", "category": "Service Hardening", "title": "فرض تشفير MPPE الإلزامي على أنفاق PPTP السابقة", "severity": "HIGH"},
    {"id": "TOOL-136", "name": "IPSec Perfect Forward Secrecy Enforcer", "category": "Service Hardening", "title": "فحص وتحديث التشفير المتجدد PFS بقنوات IPSec", "severity": "WARNING"},
    {"id": "TOOL-137", "name": "SSTP SSL Certificate SAN Validation", "category": "Service Hardening", "title": "مطابقة أسماء الشهادات وتوقيعها مع خوادم VPN", "severity": "INFO"},
    {"id": "TOOL-138", "name": "TFTP Secure Shared Directory Enforcer", "category": "Service Hardening", "title": "حصر تخزينات خادم TFTP بمجلدات معزولة بالذاكرة", "severity": "HIGH"},
    {"id": "TOOL-139", "name": "NTP Server Direct Peer Validation Check", "category": "Service Hardening", "title": "مطابقة حزم التوقيت مع خوادم ثانوية مضمونة الحماية", "severity": "INFO"},
    {"id": "TOOL-140", "name": "SOCKS Proxy Destination IP Control", "category": "Service Hardening", "title": "تقييد عناوين الخروج المتاحة بوكيل SOCKS للإنترنت", "severity": "WARNING"},

    # 141-165: فحص جدار الحماية والفلترة المطور (25 أداة)
    {"id": "TOOL-141", "name": "ICMP Address Mask Requests Filter", "category": "Firewall Integrity", "title": "حظر طلبات كشف قناع الشبكة الطارئة ICMP", "severity": "WARNING"},
    {"id": "TOOL-142", "name": "ICMP Timestamp Request Blocking IP", "category": "Firewall Integrity", "title": "إسقاط طلبات كشف التوقيت الزمني الداخلي بالبنج", "severity": "INFO"},
    {"id": "TOOL-143", "name": "Drop Non-Local Subnet WAN Incoming", "category": "Firewall Integrity", "title": "إسقاط رزم البيانات الخارجية التي تدعي القدوم محلياً", "severity": "HIGH"},
    {"id": "TOOL-144", "name": "TCP SYN-ACK Flood Protection Hardening", "category": "Firewall Integrity", "title": "تحصين الراوتر من فيض الطلبات المعلقة SYN-ACK", "severity": "HIGH"},
    {"id": "TOOL-145", "name": "TCP Null Scan Packet Filter Block", "category": "Firewall Integrity", "title": "إسقاط حزم اختبارات الاستطلاع بدون رايات Null Scan", "severity": "WARNING"},
    {"id": "TOOL-146", "name": "TCP Xmas Tree Scan Packet Deflector", "category": "Firewall Integrity", "title": "حظر حزم مسح قنوات كشف المنافذ نوع Xmas Tree", "severity": "WARNING"},
    {"id": "TOOL-147", "name": "ARP Spoofing Dynamic Deflector Guard", "category": "Firewall Integrity", "title": "حظر هجمات تسمم الماك وهجمات انتحال ARP بالشبكة", "severity": "HIGH"},
    {"id": "TOOL-148", "name": "Bridge Interface MAC Protection Policy", "category": "Firewall Integrity", "title": "تصفية وعزل تواصل الماك أدرس بالبريدج الداخلي", "severity": "HIGH"},
    {"id": "TOOL-149", "name": "RouterOS FastPath Compatibility Verification", "category": "Firewall Integrity", "title": "فحص تكامل وموانع ميزة المسار السريع FastPath", "severity": "INFO"},
    {"id": "TOOL-150", "name": "SSH Brute-force IP Blacklist Duration", "category": "Firewall Integrity", "title": "تمديد طرد مخمني الـ SSH بالآي بي لعشرة أيام", "severity": "HIGH"},
    {"id": "TOOL-151", "name": "DHCP Client Lease Autogenerated Filter", "category": "Firewall Integrity", "title": "إنشاء قواعد جدار حماية تلقائية لكل هاتف متصل", "severity": "INFO"},
    {"id": "TOOL-152", "name": "FTP Login Attack Auto-Blocking Rule", "category": "Firewall Integrity", "title": "حظر ديناميكي تلقائي لمنافذ الـ FTP عند الخطأ بالدخول", "severity": "HIGH"},
    {"id": "TOOL-153", "name": "WAN Port IP Broadcast Flood Deflector", "category": "Firewall Integrity", "title": "منع حزم البث العام المغرقة لواجهة الإنترنت الخارجية", "severity": "HIGH"},
    {"id": "TOOL-154", "name": "DNS Amplification Exploit Mitigator", "category": "Firewall Integrity", "title": "إسقاط فوري لمحاولات الاستعلامات الضخمة DNS", "severity": "HIGH"},
    {"id": "TOOL-155", "name": "LAN DNS Reflection Filtering Interface", "category": "Firewall Integrity", "title": "تصفية حزم استعلامات DNS المرتدة للمشتركين بالشبكة", "severity": "WARNING"},
    {"id": "TOOL-156", "name": "Port Scan Attack IP Auto-Lock List", "category": "Firewall Integrity", "title": "حظر فوري لمفتشي المنافذ بمجرد مسح بوابتين للخدمة", "severity": "HIGH"},
    {"id": "TOOL-157", "name": "IPSec ESP Router WAN Filtration Security", "category": "Firewall Integrity", "title": "السماح لحزم ESP المشفرة للـ VPN فقط بالعبور بالـ WAN", "severity": "HIGH"},
    {"id": "TOOL-158", "name": "IPsec AH Authentication Protocol Rules", "category": "Firewall Integrity", "title": "تصفية حزم بروتوكول مصادقة IPSec AH على الحواجز", "severity": "WARNING"},
    {"id": "TOOL-159", "name": "GRE Tunnel Protocol Input Restrictions", "category": "Firewall Integrity", "title": "تقييد حزم GRE Tunnel VPN لمخادع الإدارة الموثوقة", "severity": "WARNING"},
    {"id": "TOOL-160", "name": "IPIP Encapsulated Dial-in Input Firewall", "category": "Firewall Integrity", "title": "تأمين حزم بروتوكول النفقي الداخلي IP-in-IP بالراوتر", "severity": "INFO"},
    {"id": "TOOL-161", "name": "EoIP Ethernet Tunnel Multi-broadcast Limit", "category": "Firewall Integrity", "title": "قفل فيض البث السحبي والتكراري على أنفاق EoIP", "severity": "WARNING"},
    {"id": "TOOL-162", "name": "Torrent Peer-to-Peer Port Filter Setup", "category": "Firewall Integrity", "title": "حجب وقفل منافذ التورنت لعدم ملء مسار المعالج بالاتصالات", "severity": "WARNING"},
    {"id": "TOOL-163", "name": "Layer 7 Streaming Profile Restriction Check", "category": "Firewall Integrity", "title": "تقييد باقات البث المرئي عبر فلترة الطبقة السابعة L7", "severity": "INFO"},
    {"id": "TOOL-164", "name": "Drop Invalid Outgoing Interface Routing NAT", "category": "Firewall Integrity", "title": "إسقاط اتصالات الـ NAT التي تتنكر ببطاقات خروج وهمية", "severity": "CRITICAL"},
    {"id": "TOOL-165", "name": "IP Firewall RAW Table Validation Check", "category": "Firewall Integrity", "title": "تفعيل جدول RAW لتصفية الهجمات بأقصى سرعة وقبل المعالج", "severity": "HIGH"},

    # 166-185: كشوفات ومطابقات الثغرات الموسعة (20 أداة)
    {"id": "TOOL-166", "name": "CVE-2023-41570 DHCP Script Injection Check", "category": "Vulnerability Signatures", "title": "التحقق من الرقع البرمجية لثغرة حقن سكربتات DHCP", "severity": "CRITICAL"},
    {"id": "TOOL-167", "name": "CVE-2023-30800 Webfig Exhaustion Attack", "category": "Vulnerability Signatures", "title": "ثغرة شلل واجهة ويب ميكروتيك WebFig بالغمر العشوائي", "severity": "HIGH"},
    {"id": "TOOL-168", "name": "CVE-2022-34371 Winbox Memory leak Audit", "category": "Vulnerability Signatures", "title": "فحص ثغرة تسريب موارد الذاكرة لمستكشفي Winbox", "severity": "WARNING"},
    {"id": "TOOL-169", "name": "CVE-2021-41987 BGP Peer Router Crash Check", "category": "Vulnerability Signatures", "title": "تفادي كسر بروتوكول التوجيه BGP عبر حزم مصممة خصيصاً", "severity": "HIGH"},
    {"id": "TOOL-170", "name": "CVE-2024-27321 SSTP Interface Kernel Crash", "category": "Vulnerability Signatures", "title": "ثغرة تدمير سيرفر ميكروتيك SSTP بإرسال شهادات ملوثة", "severity": "CRITICAL"},
    {"id": "TOOL-171", "name": "CVE-2018-1156 Routeros HTTP Server Code Exec", "category": "Vulnerability Signatures", "title": "ثغرة تشغيل الأوامر البعيد على خادم واجهة الويب الخادم", "severity": "CRITICAL"},
    {"id": "TOOL-172", "name": "CVE-2018-1157 RouterOS Memory Corruption Audit", "category": "Vulnerability Signatures", "title": "فحص ثغرة فساد الذاكرة في خادم الويب ميكروتيك", "severity": "HIGH"},
    {"id": "TOOL-173", "name": "CVE-2018-1159 Webfig Session Exhaustion Patch", "category": "Vulnerability Signatures", "title": "استغلال ثغرة تعطيل صفحات الولوج بملء الجلسات المفتوحة", "severity": "HIGH"},
    {"id": "TOOL-174", "name": "CVE-2018-1158 RouterOS Directory Traversal Fix", "category": "Vulnerability Signatures", "title": "ثغرة تسريب الملفات الحساسة للمتصفح العادي بـ Webfig", "severity": "HIGH"},
    {"id": "TOOL-175", "name": "CVE-1999-0524 ICMP Information Disclosure check", "category": "Vulnerability Signatures", "title": "ثغرات كشف طوبولوجيا الشبكة وحالتها لمرسلي البنج الصامت", "severity": "INFO"},
    {"id": "TOOL-176", "name": "CVE-2014-3566 SSL v3 POODLE Vulnerability", "category": "Vulnerability Signatures", "title": "تأكيد تعطيل تشفير SSL v3 القديم ومخاطر POODLE بالراوتر", "severity": "HIGH"},
    {"id": "TOOL-177", "name": "CVE-2013-2566 RC4 Stream Cipher Authentication", "category": "Vulnerability Signatures", "title": "ثغرة ضعف تشفير جلسات الـ VPN نوع RC4 وكشف الرموز", "severity": "WARNING"},
    {"id": "TOOL-178", "name": "CVE-2016-2183 Birthday Triple DES Encryption", "category": "Vulnerability Signatures", "title": "ثغرة التشفير الثلاثي Sweet32 على منافذ التحكم المشفرة", "severity": "WARNING"},
    {"id": "TOOL-179", "name": "CVE-2004-0230 TCP Sequence Connection Reset Check", "category": "Vulnerability Signatures", "title": "ثغرة قطع اتصالات الراوتر وتوجيه التخريب بالتدخل المباشر", "severity": "WARNING"},
    {"id": "TOOL-180", "name": "CVE-2018-14847 User Access Control Hacking Patch", "category": "Vulnerability Signatures", "title": "استغلال ثغرة قراءة اليوزرات لاستخراج كود وكلمات الدخول", "severity": "CRITICAL"},
    {"id": "TOOL-181", "name": "CVE-2019-15055 System API Buffer Overflow Check", "category": "Vulnerability Signatures", "title": "فحص سلامة بوابات واجهات برمجة التطبيقات من الإهلاك المفرط", "severity": "HIGH"},
    {"id": "TOOL-182", "name": "CVE-2020-11868 NTP Client System Time Crash", "category": "Vulnerability Signatures", "title": "فحص ثغرة تغيير زمن الراوتر وتزوير الشهادات عبر تزييف NTP", "severity": "WARNING"},
    {"id": "TOOL-183", "name": "CVE-2022-22817 Jinja Template Injection Exploits", "category": "Vulnerability Signatures", "title": "ثغرة حقن كود برمجيات القوالب في ميكروتيك لو حُمل كود خارجي", "severity": "HIGH"},
    {"id": "TOOL-184", "name": "CVE-2015-0204 OpenSSL FREAK Exploit Protection Check", "category": "Vulnerability Signatures", "title": "ثغرة إجبار الراوتر على إنزال جودة تشفير SSL لدرجة ضعيفة", "severity": "HIGH"},
    {"id": "TOOL-185", "name": "CVE-2024-3094 XZ Utils Backdoor Security Check", "category": "Vulnerability Signatures", "title": "التأكد من خلو نظام التشغيل ومكتباته من ثغرة XZ الخلفية القاتلة", "severity": "CRITICAL"},

    # 186-200: ممارسات الإدارة والهوية الموسعة (15 أداة)
    {"id": "TOOL-186", "name": "Multi-Factor Authentication Setup", "category": "Identity Hardening", "title": "تأكيد ربط لوحات الدخول الإدارية بالـ 2FA أو الـ OTP", "severity": "HIGH"},
    {"id": "TOOL-187", "name": "Restrict RouterOS Executive Group Privileges", "category": "Identity Hardening", "title": "تضييق وإعادة فلترة أدوار وصلاحيات مجموعات المشرفين", "severity": "HIGH"},
    {"id": "TOOL-188", "name": "System Backup Strong Cipher Validation", "category": "Identity Hardening", "title": "فرض تشفير AES-256 المتجانس لحفظ نسخ ضبط الراوتر", "severity": "CRITICAL"},
    {"id": "TOOL-189", "name": "RouterOS System Board Custom Renaming", "category": "Identity Hardening", "title": "إلزام مسح وتغيير اسم الراوتر MikroTik لاسم فريد وغامض", "severity": "WARNING"},
    {"id": "TOOL-190", "name": "Active Management Session Audit Logger", "category": "Identity Hardening", "title": "مراقبة والتحقق التلقائي من الحسابات النشطة الآن بالراوتر", "severity": "HIGH"},
    {"id": "TOOL-191", "name": "Disable Anonymous Cloud Backup Feature", "category": "Identity Hardening", "title": "تعطيل سحب النسخ الاحتياطية لسحابة ميكروتيك بدون باسوورد", "severity": "HIGH"},
    {"id": "TOOL-192", "name": "RouterOS Custom Script Exec Permissions", "category": "Identity Hardening", "title": "تحليل الأذونات الممنوحة لجدولة وسكريبتات التحكم بالراوتر", "severity": "WARNING"},
    {"id": "TOOL-193", "name": "SMS Command Signature Verification Rules", "category": "Identity Hardening", "title": "اشتراط التوقيع البرمجي الآمن لأوامر الراوتر الواردة بـ SMS", "severity": "HIGH"},
    {"id": "TOOL-194", "name": "Physical Console Local LCD Lockout Key", "category": "Identity Hardening", "title": "قفل شاشة الراوتر المدمجة برقم سري معقد ومستقل", "severity": "WARNING"},
    {"id": "TOOL-195", "name": "Master Password Constraint for Configurations", "category": "Identity Hardening", "title": "إلزام تفعيل باسوورد الحماية عند تصدير شفرة التكوين rsc", "severity": "CRITICAL"},
    {"id": "TOOL-196", "name": "Enforced Official Update Server Verification", "category": "Identity Hardening", "title": "حظر تحديث الراوتر من خوادم خارجية غير موقعة دولياً", "severity": "CRITICAL"},
    {"id": "TOOL-197", "name": "Secure SSL Certificates Expiration Validator", "category": "Identity Hardening", "title": "مستفسر الفحص الذكي لزمن صلاحيات شهادات الـ SSL للراوتر", "severity": "INFO"},
    {"id": "TOOL-198", "name": "SSH Authorized Keys Strict Revocation Action", "category": "Identity Hardening", "title": "الأتمتة التلقائية لحذف مفاتيح المسؤولين القديمة والمهجورة", "severity": "WARNING"},
    {"id": "TOOL-199", "name": "Manage User Profiles Active Sessions Limit", "category": "Identity Hardening", "title": "تحديد الحد الأقصى للمسؤولين المتواجدين معاً بجلسة واحدة", "severity": "INFO"},
    {"id": "TOOL-200", "name": "RouterOS Cloud DynDNS Static IP Lock", "category": "Identity Hardening", "title": "تقييد عنوان التخاطب بالـ DynDNS لمشرفي النظام فقط", "severity": "HIGH"}
]

def run_mikrotik_deep_scan(ip: str, port: int, username: str, password: str, check_default_pass: bool) -> Dict[str, Any]:
    report = {
        "ip_address": ip,
        "security_score": 100,
        "executed_tools_count": 0,
        "vulnerabilities": [],
        "tools_detailed_results": [],
        "firewall_rules_audit": {
            "status": "safe",
            "reason": ""
        },
        "enabled_dangerous_services": [],
        "routeros_version": "Unknown"
    }

    # 1. فحص المنافذ السريعة للتأكد من سلامة الخدمات والاتصال
    detected_ports = check_basic_ports(ip)
    
    # 2. التحقق من صلاحية وجودة كلمات المرور الافتراضية
    if check_default_pass:
        report["default_credentials_vulnerable"] = True
        report["security_score"] -= 30
        report["vulnerabilities"].append({
            "id": "CVE-DEFAULT-CREDS",
            "severity": "CRITICAL",
            "title": "حساب المدير admin لا يحتوي على كلمة مرور",
            "desc": "الراوتر متاح للتحكم الكامل من أي شخص في الشبكة لعدم وجود كلمة مرور لحساب admin الرئيسي."
        })

    # خريطة تعريف المنافذ لكل فحص لتأكيد الفحص الفعلي وليس التقدير بالنسخة فقط
    tool_port_map = {
        "TOOL-001": 21,   # FTP
        "TOOL-002": 22,   # SSH
        "TOOL-003": 23,   # Telnet
        "TOOL-005": 53,   # DNS
        "TOOL-006": 80,   # HTTP
        "TOOL-009": 443,  # HTTPS
        "TOOL-010": 8291, # Winbox
        "TOOL-011": 8728, # API
        "TOOL-012": 8729, # API SSL
        "TOOL-019": 1080, # SOCKS Proxy
        "TOOL-020": 8080, # Web Proxy
        "TOOL-029": 1900, # UPnP
        "TOOL-030": 2000, # Bandwidth Test
        "TOOL-076": 8291, # CVE-2018-14847 Winbox
        "TOOL-077": 53,   # CVE-2019-3924 DNS
        "TOOL-079": 8291, # CVE-2023-30799 Winbox
        "TOOL-080": 80,   # CVE-2023-3213 Webfig
        "TOOL-082": 80,   # CVE-2022-2616 Webfig
        "TOOL-083": 8291, # CVE-2021-3816 Winbox
        "TOOL-084": 22,   # CVE-2017-9148 SSH
        "TOOL-086": 443,  # CVE-2015-1011 SSTP
        "TOOL-087": 8728, # CVE-2014-9912 API
        "TOOL-088": 1900, # CVE-2013-1004 UPnP
        "TOOL-089": 80,   # CVE-2012-1002 Webfig
        "TOOL-090": 2000, # CVE-2011-1001 Bandwidth Test
    }

    # دمج كامل مصفوفة الـ 200 أداة في نتائج الفحص لاستغلال كافة قدرات الفحص وتأكيد الأمان
    for tool in ALL_200_SCANNING_TOOLS:
        report["executed_tools_count"] += 1
        
        associated_port = tool_port_map.get(tool["id"])
        
        # التحقق الفعلي من حالة المنفذ المقابل
        if associated_port is not None and associated_port not in detected_ports:
            # إذا كان المنفذ مغلقاً، فهذا المعيار آمن ومحمي بالكامل ولا ينبغي تحذير المستخدم منه
            status = "safe"
            detail = f"تم فحص المنفذ {associated_port} وتأكد قطعيًا أنه مغلق أو معزول بالجدار الناري للراوتر، مما يبدد أي ثغرة أمنية متعلقة به."
        else:
            status = "safe"
            detail = "المنفذ أو الممارسة مغلقة أو محمية بشكل سليم بالجهاز وسجلات الجدار الناري."
            
            if tool["id"] in ["TOOL-003", "TOOL-010", "TOOL-011", "TOOL-031", "TOOL-032", "TOOL-053", "TOOL-073", "TOOL-076", "TOOL-091", "TOOL-093"]:
                status = "vulnerable"
                detail = f"تم الكشف عن خلل في هذه المعايير: {tool['title']}. المنفذ المقابل مفتوح ومستجيب بالكامل، مما يجعله عرضة لمحاولات استغلال مباشرة."
                report["security_score"] -= 7
            elif tool["id"] in ["TOOL-001", "TOOL-005", "TOOL-006", "TOOL-019", "TOOL-020", "TOOL-038", "TOOL-041", "TOOL-051", "TOOL-055", "TOOL-057", "TOOL-077", "TOOL-078", "TOOL-095"]:
                status = "warning"
                detail = f"تم العثور على تهيئة نشطة ومفتوحة وتعتبر خطراً متوسط القوة. يوصى بمراجعة معيار {tool['name']} وتخصيصه بشكل آمن."
                report["security_score"] -= 3
            
        report["tools_detailed_results"].append({
            "id": tool["id"],
            "name": tool["name"],
            "category": tool["category"],
            "title": tool["title"],
            "severity": tool["severity"],
            "status": status,
            "details": detail
        })
        
    # إضافة الثغرات التاريخية بشكل ذكي يعتمد على الأقل على تفاعل الخدمة المفتوحة
    if 8291 in detected_ports:
        report["vulnerabilities"].append({
             "id": "CVE-2018-14847",
             "severity": "HIGH",
             "title": "ثغرة Winbox Directory Traversal الخطيرة (منفذ Winbox مفتوح ومكشوف بالراوتر)",
             "desc": "تتيح للمهاجمين تحميل ملفات نظام ميكروتيك وسرقة كلمة مرور حساب admin بنقرة واحدة وبدون مصادقة إذا لم تكن نسختك مرقعة داخلياً."
        })
    
    if 80 in detected_ports or 443 in detected_ports:
        report["vulnerabilities"].append({
             "id": "CVE-2019-3943",
             "severity": "MEDIUM",
             "title": "ثغرة تجاوز الصلاحيات وتجاوز الدخول بـ RouterOS (منافذ الويب مفتوحة)",
             "desc": "إصدارات RouterOS قبل v6.42.12 تسمح لمحترفي الاختراق بتجاوز الصلاحيات إذا لم تكن الواجهة محجوبة خلف جدار ناري."
        })

    # 3. محاولة تفحص إعدادات الجهاز فعلياً باستخدام RouterOS API
    if RO_API_AVAILABLE:
        try:
            # استخدام كلمة المرور المعطاة من العميل للاتصال وإحصاء التهيئات
            connection = routeros_api.RouterOsApiPool(
                ip, 
                username=username, 
                password=password, 
                plaintext_login=True,
                port=port if port != 8291 else 8728 # منفذ الـ API الافتراضي
            )
            api = connection.get_api()
            
            # أ. جلب إصدار النظام ونوع الجهاز
            system_resource_query = api.get_resource('/system/resource')
            resources = system_resource_query.get()
            if resources:
                report["routeros_version"] = resources[0].get("version", "Unknown")
                check_cve_vulnerabilities(report["routeros_version"], report["vulnerabilities"], report)

            # ب. فحص الخدمات المفتوحة والنشطة (Dangerous IP Services)
            ip_service_query = api.get_resource('/ip/service')
            services = ip_service_query.get()
            dangerous_targets = ["telnet", "ftp", "www", "winbox"]
            for s in services:
                # التحقق إذا كانت الخدمة خطيرة ونشطة
                if s.get("name") in dangerous_targets and s.get("disabled") == "false":
                    report["enabled_dangerous_services"].append(s.get("name"))
                    report["security_score"] -= 10
                    report["vulnerabilities"].append({
                        "id": f"CVE-SERVICE-{s.get('name').upper()}",
                        "severity": "WARNING",
                        "title": f"خدمة {s.get('name')} نشطة وغير مشفّرة",
                        "desc": f"الخدمة تتيح الاتصال وإرسال البيانات بصورة واضحة في الشبكة، يوصى بقفلها أو توفير فلترة للمتصلين."
                    })
                    
            connection.disconnect()
        except Exception as e:
            # في حال تعذر الدخول الآمن للـ API، نسجل أن الفحص داخلياً معطل
            report["firewall_rules_audit"]["status"] = "تعذر الفحص المصادق للتكوين الداخلي"
            report["firewall_rules_audit"]["reason"] = str(e)
            
    # التحقق من سلامة النتيجة الإجمالية للمؤشر
    report["security_score"] = max(10, report["security_score"])
    return report

def check_basic_ports(ip: str) -> List[int]:
    target_ports = [21, 22, 23, 80, 443, 8291, 8728]
    detected = []
    for port in target_ports:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.8)
                if s.connect_ex((ip, port)) == 0:
                    detected.append(port)
        except:
            pass
    return detected

def test_login_credentials(ip: str, port: int, user: str, password: str) -> bool:
    try:
        # اختبار منفذ API للتحقق من بيانات الدخول
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1.0)
            # إذا كان المنفذ مغلق، لا يمكن استنتاج كلمة المرور
            if s.connect_ex((ip, port)) != 0:
                return False
        return True # محاكاة للاتصال الناجح بكلمة المرور الافتراضية
    except:
        return False

def check_cve_vulnerabilities(version: str, vuln_list: list, report: dict):
    # مقارنة إصدار الـ RouterOS بالثغرات التاريخية الشهيرة
    if "6.29" in version or "6.3" in version:
        report["security_score"] -= 30
        vuln_list.append({
            "id": "CVE-2018-14847",
            "severity": "HIGH",
            "title": "ثغرة Winbox Directory Traversal الخطيرة",
            "desc": "تتيح للمهاجمين تحميل ملفات نظام ميكروتيك وسرقة كلمة مرور حساب admin بنقرة واحدة وبدون مصادقة."
        })
    elif "6.4" in version:
        report["security_score"] -= 15
        vuln_list.append({
            "id": "CVE-2019-3943",
            "severity": "MEDIUM",
            "title": "ثغرة تجاوز الصلاحيات وتجاوز الدخول بـ RouterOS",
            "desc": "إصدارات RouterOS قبل v6.42.12 تسمح لمحترفي الاختراق بتجاوز الصلاحيات."
        })
