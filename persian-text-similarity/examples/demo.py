from persian_text_similarity import TfidfIndex, normalize

print(normalize("كتاب‌های فارسی ۱۲۳"))
index = TfidfIndex(["گزارش پروژه آماده است", "خرید کتاب فارسی", "جلسه بررسی پروژه"])
for match in index.search("گزارش پروژه", top_k=2):
    print(f"{match.score:.3f}\t{match.text}")
