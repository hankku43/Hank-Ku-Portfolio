from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    vehicle_model_path: str = "models/vehicle_detection_model_5.pth"
    digit_model_path: str = "models/digit_recognition.pth"
    ptt_model_path: str = "models/ptt_classifier.pth"
    ptt_doc2vec_path: str = "models/ptt_titles_doc2vec_ver3.model"
    rag_doc2vec_path: str = "models/traffic_law_doc2vec.model"
    rag_csv_path: str = "models/traffic_law_articles.csv"
    classical_nlp_model_path: str = "models/classical_chinese_lm.pth"
    ollama_base_url: str = "http://localhost:11434"
    cors_origins: list[str] = ["*"]

    class Config:
        env_file = ".env"


settings = Settings()
