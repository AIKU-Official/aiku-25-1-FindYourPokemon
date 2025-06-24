# model.py

import numpy as np
import json
import torch
import faiss
from transformers import AutoTokenizer, AutoModel, AutoProcessor, AutoModelForZeroShotImageClassification
from PIL import Image

# 경로 설정 (레포 최상위 기준)
root_dir = "."   # 현재 폴더

image_folder = f"{root_dir}/dataset/pokemonimage"
metadata_path = f"{root_dir}/dataset/pokemon_metadata_full.json"
sbert_emb_path = f"{root_dir}/embeddings/krsbert_text_embeddings.npy"
clip_emb_path  = f"{root_dir}/embeddings/clip_image_embeddings.npy"
sbert_index_path = f"{root_dir}/embeddings/sbert.index"
clip_index_path  = f"{root_dir}/embeddings/clip.index"


# 데이터/메타데이터 로드
sbert_text_embeddings = np.load(sbert_emb_path, allow_pickle=True).item()
clip_img_embeddings   = np.load(clip_emb_path, allow_pickle=True).item()
id_list = list(sbert_text_embeddings.keys())

with open(metadata_path, encoding="utf-8") as f:
    metadata = json.load(f)
id2meta = {entry['id']: entry for entry in metadata}

# 모델 초기화
sbert_tokenizer = AutoTokenizer.from_pretrained("snunlp/KR-SBERT-V40K-klueNLI-augSTS")
sbert_model = AutoModel.from_pretrained("snunlp/KR-SBERT-V40K-klueNLI-augSTS")

clip_processor = AutoProcessor.from_pretrained("Bingsu/clip-vit-large-patch14-ko")
clip_model = AutoModelForZeroShotImageClassification.from_pretrained("Bingsu/clip-vit-large-patch14-ko")

# 임베딩 함수
def sbert_encode(text):
    encoded_input = sbert_tokenizer(text, padding=True, truncation=True, return_tensors='pt')
    with torch.no_grad():
        model_output = sbert_model(**encoded_input)
    embeddings = model_output.last_hidden_state
    attention_mask = encoded_input['attention_mask']
    mask = attention_mask.unsqueeze(-1).expand(embeddings.size()).float()
    masked_embeddings = embeddings * mask
    summed = torch.sum(masked_embeddings, 1)
    counts = torch.clamp(mask.sum(1), min=1e-9)
    mean_pooled = summed / counts
    return mean_pooled[0].cpu().numpy()

def clip_text_encode(text):
    inputs = clip_processor(text=[text], return_tensors="pt", padding=True)
    with torch.no_grad():
        text_emb = clip_model.get_text_features(**inputs)
    return text_emb[0].cpu().numpy()

# FAISS 인덱스 불러오기
sbert_index = faiss.read_index(sbert_index_path)
clip_index  = faiss.read_index(clip_index_path)

def pokemon_search(user_query, topn=5, alpha=0.3, beta=0.7):
    # 1. SBERT 임베딩
    sbert_query_emb = sbert_encode(user_query)
    sbert_query_emb = sbert_query_emb / np.linalg.norm(sbert_query_emb)
    # 2. CLIP 임베딩
    clip_query_emb = clip_text_encode(user_query)
    clip_query_emb = clip_query_emb / np.linalg.norm(clip_query_emb)

    # 3. top-k 후보군
    k = 50
    _, sbert_top_idx = sbert_index.search(sbert_query_emb[np.newaxis, :].astype(np.float32), k)
    _, clip_top_idx  = clip_index.search(clip_query_emb[np.newaxis, :].astype(np.float32), k)
    candidate_idx = set(sbert_top_idx[0]) | set(clip_top_idx[0])
    candidate_ids = [id_list[idx] for idx in candidate_idx]

    # 4. 결합 점수 계산
    final_scores = {}
    for pid in candidate_ids:
        sbert_score = np.dot(sbert_query_emb, sbert_text_embeddings[pid])
        clip_score  = np.dot(clip_query_emb, clip_img_embeddings[pid])
        final_scores[pid] = alpha * sbert_score + beta * clip_score

    # 5. Top N 추출
    topn_results = sorted(final_scores.items(), key=lambda x: x[1], reverse=True)[:topn]
    images, names, descs = [], [], []
    for pid, score in topn_results:
        info = id2meta[pid]
        name = f"{info['name']} ({pid}) - 점수: {score:.4f}"
        desc = info.get("full_description_ko", "")
        img_path = f"{image_folder}/{pid}.png"
        try:
            img = Image.open(img_path).convert("RGBA")
        except:
            img = Image.new("RGBA", (256,256), (255,255,255,0))
        images.append(img)
        names.append(name)
        descs.append(desc)
    return images, "\n".join(names), "\n\n".join(descs)
