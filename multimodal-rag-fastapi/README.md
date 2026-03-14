# Multimodal RAG FastAPI

Bu proje, terminal (CLI) tabanlı RAG (Retrieval-Augmented Generation) mimarisinin bir adım öteye taşınmış, **FastAPI** ve **Weaviate** Vector Veritabanı ile güçlendirilmiş, üretime (production) daha hazır bir REST API versiyonudur.

## 🎯 Hedefimiz (Amacımız)

- RAG mantığını yalnızca terminalde çalışan bir betikten çıkarıp, web tabanlı veya mobil uygulamaların (örneğin uç birimdeki React/Tailwind bir uygulamanın) rahatça istek (HTTP Request) atabileceği bir API haline getirmek.
- RAM'de geçici veri tutmak yerine, belgelerin vektörel karşılıklarını (embeddingleri) **Weaviate** kullanarak kalıcı (persistent) hale getirmek ve böylece sunucu her yeniden başladığında baştan hesaplama yapma külfetinden kurtulmak.
- Asenkron **BackgroundTasks** kullanarak uzun süren vektörleştirme (embedding) işlemlerinin API'yi bloke etmesinin (kilitlenmesinin) önüne geçmek.

## 🧠 Ne Öğrendik?

- **Vector DB Kalıcılığı:** `weaviate-haystack` entegrasyonu ile yerel bir Docker Weaviate konteynerine nasıl bağlanılacağını ve belgelerin nasıl kalıcı hale getirileceğini.
- **Idempotency (Tekrarlanabilirlik Kontrolü):** `filter_documents` kullanarak bir belgenin (örneğin X makalesi) veritabanında zaten olup olmadığını kontrol etmeyi ve varsa aynı belgeyi tekrar vektörleştirmekten kaçınmayı (maliyet ve zaman tasarrufu).
- **FastAPI Background Tasks:** Kullanıcı belgelere embedding işlemi başlattığında, işlemin arka planda devam etmesini ve kullanıcıya hemen "İşlem başladı" yanıtı dönmesini sağlamayı.
- **Durum (State) Yönetimi:** Eğer vektörleştirme arka planda hala devam ediyorsa, `/api/query` ucunun kullanıcıyı güvenli bir şekilde `"Embedding still working please wait 5 minutes to try again"` mesajıyla bloke etmeden uyarmasını sağlamayı.
- **Güvenli Kod Standartları:** `ruff` formatter ve linter kullanarak temiz ve standartlara (PEP8) uygun modern Python kodu yazmayı.

## 🚀 Neler Yaptık?

1. FastAPI ile `/api/embed` (Dokümanları veritabanına işleyen) ve `/api/query` (Soru sormaya yarayan) iki adet endpoint (uç nokta) oluşturduk.
2. `InMemoryDocumentStore` yapısını `WeaviateDocumentStore` ile değiştirdik. Lokal çalıştırmak için bir Weaviate Docker konteyneri ayağa kaldırdık.
3. `rag_service.py` içerisinde Haystack Pipeline'ı kurarak, Google Gemini (`gemini-embedding-2-preview` ve `gemini-3.1-flash-lite-preview`) modelleriyle sistemi entegre ettik.
4. `/api/embed` uç noktasını asenkron bir görev (Background Task) haline getirdik.
5. `tests/test_api.py` ve `tests/test_services.py` dosyalarında birim testleri güncelleyerek mock (sahte) nesneler üzerinden test edilebilir bir kod inşa ettik.

## ⚙️ Kurulum ve Kullanım (uv ile)

Proje, bağımlılıkları yönetmek için `uv` kullanmaktadır.

1. **Bağımlılıkları Yükleyin**
Ana dizinde Terminali açıp aşağıdaki komutu çalıştırın:

```bash
uv sync 
# Veya alternatif olarak: uv pip install -r pyproject.toml / uv.lock mantığıyla
```

1. **Çevre Değişkenlerini (Environment Variables) Ayarlayın**
`.env` adında bir dosya oluşturun ve Google Gemini API bilginizi ekleyin:

```bash
GEMINI_API_KEY=sizin-api-anahtariniz
```

1. **Weaviate Veritabanını Başlatın**
Belgelerin vektör verilerinin saklanması için Weaviate çalışıyor olmalıdır. Sisteme ait Weaviate'i ayağa kaldırmak için aşağıdaki (güncel 1.36.2) Docker komutunu çalıştırın:

```bash
docker run -d -p 8080:8080 -p 50051:50051 --name weaviate \
-e QUERY_DEFAULTS_LIMIT=25 \
-e AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED=true \
-e DEFAULT_VECTORIZER_MODULE=none \
-e CLUSTER_HOSTNAME=node1 \
cr.weaviate.io/semitechnologies/weaviate:1.36.2
```

1. **FastAPI Sunucusunu Başlatın**
API'yi aktif etmek için Uvicorn üzerinden sunucuyu ayağa kaldırın:

```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

1. **API Kullanımı (Terminalden cURL ile Test Etme)**

Önce belgeleri veritabanına tanımlamak (Vektörleştirmek) için aşağıdaki POST isteğini atın:

```bash
curl -X POST http://127.0.0.1:8000/api/embed
# Beklenen Çıktı: {"message":"Embedding process started in the background. Please wait."}
```

*(Arka planda belgeler Vector DB'ye kayıt olacaktır. Klasördeki `documents/` içindeki PDF dosyalarına `filter_documents` uygulanacak, eğer zaten Weaviate'de varsa otomatik es geçilecektir. Bu işlem bittikten sonra sorular sorabilirsiniz.)*

Soru sormak için aşağıdaki JSON Body ile POST isteğini atın:

```bash
curl -s -X POST -H "Content-Type: application/json" -d '{"question":"What is Sematic Information Extraction?"}' http://127.0.0.1:8000/api/query
```

Eğer işlem arka planda hala devam ediyorsa şu dönütü alırsınız:

```json
{"answer":"Embedding still working please wait 5 minutes to try again","documents":[]}
```

İşlem bittikten sonra tam cevabı alırsınız.
