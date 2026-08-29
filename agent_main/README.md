# Risk-Driven Agent Orchestration

Bu proje, müşteri başvurusunu güvenlik, finansal ve kredi riskine göre değerlendiren deterministik bir agent pipeline örneğidir.

## Akış

```text
User Request
  -> Input Validation & Data Minimization
  -> Document Analyzer
  -> Decision Orchestrator
      -> Financial Analyzer
      -> Fraud / Security Agent
      -> Credit Risk Agent
  -> Evidence Aggregation
  -> Policy Validator
  -> Authorized Action Layer
  -> Final Decision
```

## Katmanlar

- Input Validator: Metin içinde PII verilerini maskeler ve veriyi minimize eder.
- Document Analyzer: Doğal dil girdisini yapılandırılmış verilere çevirir.
- Decision Orchestrator: Tüm ajanlardan gelen kanıtları birleştirir.
- Financial Agent: Gelir/borç oranlarını deterministik kurallarla değerlendirir.
- Fraud Agent: Sahtecilik ve abuse sinyallerini kontrol eder.
- Credit Agent: Çalışma süresi ve gelir bazlı risk üretir.
- Policy Validator: LLM çıktısını şema ve kural seti ile denetler.
- Authorized Action Layer: Yalnızca onaylanan eylemleri üretir.

## Çalıştırma

```bash
python main.py
```

`input.txt` dosyasındaki başvuru metnini kullanarak risk kararını üretir.
