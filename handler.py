import os
import json
import urllib.request
import runpod

# ComfyUI 서버 주소 (로컬 구동 시)
COMFY_HOST = "127.0.0.1:8188"

def queue_prompt(workflow):
    p = {"prompt": workflow}
    data = json.dumps(p).encode('utf-8')
    req = urllib.request.Request(f"http://{COMFY_HOST}/prompt", data=data)
    return json.loads(urllib.request.urlopen(req).read())

def handler(job):
    job_input = job['input']
    
    # 클라이언트로부터 전달받은 이미지 파일명 또는 경로 설정
    # (클라이언트가 입력값으로 image_1, image_2를 보낸다고 가정)
    base_image = job_input.get("image_1", "default_base.jpg")
    ref_image = job_input.get("image_2", "default_ref.jpg")

    # 1. API 형식의 워크플로우 JSON 로드
    with open("headswap_api.json", "r", encoding="utf-8") as f:
        workflow = json.load(f)

    # 2. 워크플로우 내에서 LoadImage 노드(76번, 81번)의 파일명 동적 변경
    # 앞서 분석한 JSON 구조 기준: 76번 = Base 이미지, 81번 = Reference 이미지
    if "76" in workflow:
        workflow["76"]["inputs"]["image"] = base_image
    if "81" in workflow:
        workflow["81"]["inputs"]["image"] = ref_image

    # 3. ComfyUI로 워크플로우 실행 요청 전송
    response = queue_prompt(workflow)
    prompt_id = response.get("prompt_id")

    # 결과 반환 (실제 구현 시 완료 대기 및 이미지 다운로드 로직 추가 필요)
    return {
        "status": "success",
        "prompt_id": prompt_id,
        "message": "Workflow queued successfully on RunPod Serverless."
    }

runpod.serverless.start({"handler": handler})