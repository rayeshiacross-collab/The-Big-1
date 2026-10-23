"""Explicit protocol, bounded retries and strict local-only model transport."""
import time
import requests
from .config import LOCAL_MODEL_BASE_URL, LOCAL_MODEL_NAME, LOCAL_MODEL_PROTOCOL, assert_open_stack
class LocalModelError(Exception): pass

def chat(messages, *, model=None, temperature=0.4, max_tokens=2048):
    assert_open_stack()
    url = LOCAL_MODEL_BASE_URL.rstrip('/')
    model = model or LOCAL_MODEL_NAME
    if LOCAL_MODEL_PROTOCOL == 'ollama':
        endpoint = url.removesuffix('/v1') + '/api/chat'
        payload = dict(model=model, messages=messages, stream=False, options=dict(temperature=temperature, num_predict=max_tokens))
    else:
        endpoint = url if url.endswith('/v1') else url + '/v1'
        endpoint += '/chat/completions'
        payload = dict(model=model, messages=messages, temperature=temperature, max_tokens=max_tokens)
    # Ignore proxy environment and reject redirects; neither may reroute local prompts.
    with requests.Session() as session:
        session.trust_env = False
        for attempt in range(3):
            try:
                r = session.post(endpoint, json=payload, timeout=(5, 300), allow_redirects=False)
                if r.status_code in {429, 500, 502, 503, 504} and attempt < 2:
                    time.sleep(0.25 * (attempt + 1)); continue
                if r.status_code != 200: raise LocalModelError(f'Model returned HTTP {r.status_code}')
                data = r.json()
                result = data['message']['content'] if LOCAL_MODEL_PROTOCOL == 'ollama' else data['choices'][0]['message']['content']
                if not isinstance(result, str) or not result.strip(): raise ValueError('Empty model reply')
                return result
            except (requests.ConnectionError, requests.Timeout) as e:
                if attempt == 2: raise LocalModelError('Local model unreachable after 3 attempts') from e
                time.sleep(0.25 * (attempt + 1))
            except (ValueError, KeyError, IndexError, TypeError) as e:
                raise LocalModelError('Malformed local model reply') from e

def doctor_check():
    try:
        reply = chat([dict(role='user', content='Reply with exactly: OK')], max_tokens=8, temperature=0)
        return dict(reachable=True, ok=reply.strip() == 'OK', sample=reply[:80])
    except Exception as e:
        return dict(reachable=False, ok=False, error=str(e))
