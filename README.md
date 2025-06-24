# Pokemon is Worth 16x16 Words

📢 2025년 1학기 [AIKU](https://github.com/AIKU-Official) 활동으로 진행한 프로젝트입니다

## 소개
> 포켓몬의 설명만 입력하면 어떤 포켓몬인지 찾아주는 것이 목표

본 프로젝트는 사용자가 포켓몬의 외형이나 특징을 한국어로 자유롭게 묘사하면, 포켓몬 중 가장 유사한 포켓몬을 찾아주는 검색 시스템을 구현한 것입니다.  
포켓몬 공식 도감의 데이터를 기반으로, 배경 없는 이미지와 메타데이터(이름, 타입, 분류, 외형 설명 등)를 구축했습니다.  
한국어로 입력되는 외형 묘사는 한국어 SBERT, CLIP 모델로 임베딩하여, 도감 전체 이미지 및 설명과 유사도 기반으로 매칭하며,  
빠른 검색을 위해 FAISS 인덱싱을 적용했습니다.    
최종적으로 Gradio 기반 웹 데모로 누구나 실시간 검색과 시각적 결과 확인이 가능합니다.  

## 방법론
> 텍스트·이미지 임베딩을 결합한 멀티모달 의미 기반 검색 파이프라인을 도입함으로써,
> 자유로운 한국어 묘사로 원하는 포켓몬을 쉽고 정확하게 찾을 수 있도록 설계하였습니다.
<img width="1197" alt="image" src="https://github.com/user-attachments/assets/25871b7c-02f5-45dd-90cb-8b5519e35e2e" />


### 1. 데이터셋 구축
- [포켓몬 공식 도감](https://pokemonkorea.co.kr/pokedex)에서 포켓몬 이미지와 이름, 타입, 분류 등 기본 정보 수집 후,
  각 포켓몬의 외형을 설명한 한국어 문장 (메타데이터) 추가 처리
- 이미지와 외형 설명이 1:1로 매칭된 커스텀 데이터셋 구축

### 2. Embedding Extraction
- **text embedding**  
  사용자 입력 및 포켓몬 description을 KR-SBERT((snunlp/KR-SBERT-V40K-klueNLI-augSTS)로 임베딩 하여 768차원 벡터로 변환
    
- **image embedding**  
  포켓몬 이미지를 한글 prompt를 지원하는 CLIP(Bingsu/clip-vit-large-patch14-ko) 모델로 임베딩
    
- 모든 임베딩 벡터는 L2 normalization 후, FAISS indexing에 활용됨

### 3. Multimodal Similarity Search Pipeline
- FAISS index에 텍스트 및 이미지 임베딩을 저장하여 빠른 nearest neighbor search가 가능하도록 함
    
- pokemon description에 대해 SBERT와 CLIP 각각의 임베딩을 추출하여 두 인덱스에서 top-K candidates 검색
    
- 각 후보군에 대해 cosine similarity 점수를 산출하고, 사전 정의된 가중치(α for SBERT, β for CLIP)로 결합하여 Top-N 결과를 출력
    

## 환경 설정
```
pip install -r requirements.txt
```

(Requirements, Anaconda, Docker 등 프로젝트를 사용하는데에 필요한 요구 사항을 나열해주세요)

## 사용 방법

(프로젝트 실행 방법 (명령어 등)을 적어주세요.)

## 예시 결과
사용자가 입력한 자유로운 외형 묘사에 대해 가장 유사한 포켓몬 Top-5 이미지를 빠른 시간 안에 이름/설명과 함께 실시간 시각화

![image](https://github.com/user-attachments/assets/504553bd-316b-4bf4-8489-18be52ca019c)

## 팀원

  | 팀원                            | 역할                                       |
| ----------------------------- | ---------------------------------------- |
| [김승주](https://github.com/topsecretjuju) |    프로젝트 총괄, 데이터 크롤링, 파이프라인 설계    |
| [윤혜원](https://github.com/yoonewon)     |    데이터 처리 / 정제, 임베딩 추출 및 성능 평가     |
| [이시현](https://github.com/thissihyun)        |    데이터 정제, gradio 데모 구현    |
| [지세현](https://github.com/sehyeonji321)        |    데이터 처리 / 정제, 모델 성능 고도화   |
