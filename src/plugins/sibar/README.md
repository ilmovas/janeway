## Sibar — Research Integrity Plugin for Janeway / سبار — بلوقن النزاهة البحثية لـ Janeway

### نظرة عامة
بلوقن **سِبار (Sibar)** هو بلوقن مراحل سير عمل (Workflow) لمنصّة **Janeway** يدمج خدمة سِبار للنزاهة البحثية ضمن سير عمل تحرير المجلة. يعمل كمرحلة ضمن سير العمل **قبل التحكيم** لمساعدة هيئة التحرير على تقييم سلامة البحث قبل متابعة المراحل التالية.

### Overview
**Sibar** is a Janeway **workflow-stage plugin** that integrates the Sibar research-integrity service into a journal’s editorial workflow. It runs as a workflow stage **before peer review** to support editorial screening prior to advancing submissions.

### المزايا / Features (five layers)
1. **كشف التكرار/التشابه عبر الإنترنت** (الانتحال/النشر المكرر).
2. **سجل الباحث عبر ORCID** (المنشورات، مؤشرات خطر “salami publishing”).
3. **سلامة المراجع عبر التحقق من DOI**.
4. **درجة نزاهة إجمالية مع توصية تحريرية**.
5. **تقرير PDF رسمي بعلامة المجلة** يمكن إرفاقه بقرار التحرير.

### المتطلبات / Requirements
- **Janeway**: ‏**1.7.0+** (تم اختباره على **1.8.0**).
- **Python dependency**: ‏`weasyprint==69.0`
  - في إعدادات Janeway القياسية عبر Docker، يتم تثبيت متطلبات البلوقن تلقائياً من ملف `requirements.txt` داخل البلوقن.
- **System libraries (WeasyPrint runtime)**: ‏**pango**, **cairo**, **gdk-pixbuf**
  - هذه المكتبات متوفرة عادةً ضمن صورة Janeway القياسية، لكن يجب توثيقها كمتطلبات في البيئات المخصصة.
- **Sibar API access**: تحتاج المجلة إلى **Sibar API Base URL** و **Sibar API Key** صالحين.

### ملاحظة حول الاشتراك / Subscription note
يتطلب البلوقن اشتراكاً/صلاحية وصول إلى خدمة سِبار عبر مفتاح API. **تواصل مع مزوّد خدمة سِبار لديك للحصول على مفتاح API**.

### الإصدار / Version
**0.1**
