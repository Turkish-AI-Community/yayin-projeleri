# Multimodal RAG CLI

Bu proje, terminal (CLI) üzerinden çalışan basit ama güçlü bir Retrieval-Augmented Generation (RAG) uygulamasıdır. Amacı, PDF belgelerini okuyup parçalara ayırmak, Google Gemini'nin Embedding (Gömme) modellerini kullanarak bu parçaları anlamlandırmak ve kullanıcının sorduğu sorulara bu belgeler ışığında cevaplar üretmektir.

## 🎯 Hedefimiz (Amacımız)

- Belirli dokümanlardan (örneğin akademik makaleler) bilgi çekmek ve doğru cevaplar üreten bir asistan oluşturmak.
- **Haystack** kütüphanesini kullanarak modern bir RAG (Retrieval-Augmented Generation) altyapısının nasıl kurulduğunu kavramak.
- Google'ın **Gemini Multimodal Embedding** ve **Flash Lite** modelleriyle metin bazlı soru-cevap mekaniklerini test etmek.

## 🧠 Ne Öğrendik?

- **Doküman Parçalama (Chunking):** Uzun PDF belgelerinin bellek tüketimini azaltmak için belirli sayfa aralıklarıyla nasıl bölüneceğini (`split_pdf_into_chunks`).
- **InMemory Document Store:** Belgeleri ve onların vektör karşılıklarını (embedding) RAM üzerinde geçici olarak nasıl tutacağımızı.
- **Gemini Entegrasyonu:** `GoogleGenAIMultimodalDocumentEmbedder` ve `GoogleGenAITextEmbedder` ile belge ve sorgu (query) vektörizasyon işlemlerini.
- **RAG Pipeline (Boru Hattı):** Retriever ve LLM (Büyük Dil Modeli) komponentlerini birbirine bağlayarak kullanıcıdan gelen soruyu doküman bağlamıyla zenginleştirip LLM'e nasıl sunacağımızı.

## 🚀 Neler Yaptık?

1. `/documents` klasörüne bazı araştırma makaleleri (PDF) ekledik.
2. `temp.py` içerisinde `pypdf` kütüphanesi yardımıyla bu makaleleri 6 sayfalık küçük geçici PDF'lere böldük.
3. Bu parçaları okuyup `InMemoryDocumentStore` içerisine yerleştirdik.
4. Terminal üzerinden çalışan ve kullanıcının sürekli soru sorabileceği bir `while True` döngüsü (Chat Loop) kurduk.
5. Her soruda, soru metnini embedding'e çevirip vektör veritabanımızda en yakın 4 döküman parçasını (chunk) eşleştirdik ve bunu LLM'e (Gemini) yönlendirerek bir cevap ürettik.

## ⚙️ Kurulum ve Kullanım (uv ile)

Proje, bağımlılıkları ve sanal ortamları hızlıca yönetmek için **uv** kullanmaktadır.

1. **Gereksinimleri Yükleyin**
Aşağıdaki komutla `uv` üzerinden bağımlılıkları kurabilirsiniz:

```bash
uv pip install -r requirements.txt
```

1. **Çevre Değişkenleri (Environment Variables)**
Projenin çalışması için Google Gemini API Anahtarına ihtiyacınız var. Ana dizinde `.env` dosyası oluşturun ve içerisine anahtarınızı ekleyin:

```bash
GEMINI_API_KEY=sizin-api-anahtariniz
```

1. **Uygulamayı Çalıştırın**
Terminalden aşağıdaki komutu girerek uygulamayı başlatabilirsiniz:

```bash
uv run temp.py
```

Uygulama önce belgeleri okuyacak, embedding (vektörleştirme) işlemini yapacak ve ardından "Sen:" diyerek sizden soru bekleyecektir. Soru sorabilir veya çıkmak için `q` yazabilirsiniz.
