# Türkiye Yapay Zeka Topluluğu - Canlı Yayın Projeleri

Bu depo (repository), **Türkiye Yapay Zeka Topluluğu YouTube Kanalında** gerçekleştirdiğimiz canlı yayınlarda geliştirdiğimiz projeleri depolamak ve açık kaynaklı olarak paylaşmak amacıyla oluşturulmuştur. Yayında yazdığımız tüm projeler burada farklı klasörler halinde tutulacaktır. Bu projeleri kendi lokal geliştirme (local dev) ortamınızda kolaylıkla inceleyebilir, çalıştırabilir ve üstüne eklemeler yapabilirsiniz.

## 📺 Yayın 1: Modern RAG Sistemleri (Gemini 2 + Haystack + Weaviate)

Bu serinin yayınlanan ilk bölümünde, en güncel Google Gemini modellerini (`gemini-embedding-2-preview` ve `gemini-3.1-flash-lite-preview`) kullanarak baştan sona doküman bazlı soru-cevap asistanı (Retrieval-Augmented Generation / RAG) inşa ettik. 

Geleneksel langcahin vs yapılarından sıyrılarak modüler framework olan **Haystack**'i kullandık ve yerel bellekten başlayıp, gerçek bir Vektör Veritabanı olan **Weaviate**'e geçiş sürecini ele aldık.

Projeler iki farklı aşama/klasör olarak kurgulandı:

1. **[Terminal (CLI) RAG Uygulaması](./multimodal-rag-cli):**
   - Sadece Python üzerinde InMemoryDocumentStore kullanarak PDF bölme ve basit Q&A sistemlerinin en temel haliyle nasıl yazıldığını anlattığımız başlangıç dosyalarımız. Buradan RAG mimarisinin teorisini test edebilirsiniz. 
   
2. **[FastAPI ve Weaviate Entegreli Modern RAG](./multimodal-rag-fastapi):**
   - İlk projenin gelişmiş versiyonudur. İçerisinde FastAPI ile endpoint mimarisi kurulmuş, Uvicorn ile sunucu ayağa kaldırılmış ve In-Memory olan veri deposu yerel bir *Weaviate Docker* konteynerına bağlanmıştır. Ayrıca arka planda (BackgroundTasks) çalışan vektörizasyon ve idempotency (Aynı dosyayı tekrar yüklememe) mekanizmaları bulunmaktadır.

🔗 **[İlgili YouTube Canlı Yayınını Buradan İzleyebilirsiniz](https://www.youtube.com/live/lqS51ek4azw?si=UWrzPDECqMb8h9Wg)**

---

*Topluluğa katılıp kod üzerinden konuşmak ve tartışmak için bizi YouTube ve diğer sosyal platformlardan takip etmeyi unutmayın!*