import re, random, math, json, pickle
from collections import Counter, defaultdict

EMOTION_WORDS = {
    "sad":     {"sad","unhappy","depressed","crying","tears","grief","lonely","alone",
                "hopeless","miserable","hurt","pain","heartbroken","miss","lost"},
    "anxious": {"anxious","anxiety","worried","nervous","scared","fear","panic","stress",
                "stressed","overwhelmed","uneasy","tense","afraid","paranoid"},
    "angry":   {"angry","furious","rage","mad","frustrated","irritated","annoyed",
                "hateful","disgusted","outraged","betrayed","bitter"},
    "happy":   {"happy","excited","great","wonderful","amazing","promoted","promotion",
                "celebrate","joy","thrilled","delighted","proud","achieved","won"},
}

FALLBACKS = {
    "sad": [
        "I am really sorry you are feeling this way. You do not have to carry this alone. What has been happening?",
        "That sounds really painful, and your feelings are completely valid. What happened?",
        "I hear you. It is okay to feel sad. Do you want to tell me more about what is going on?",
    ],
    "anxious": [
        "That sounds really tough. Anxiety can feel overwhelming without a clear trigger. Can you tell me more?",
        "I hear you. That unsettled feeling is exhausting. What has been going on for you?",
        "You are not alone in this. What does the anxiety feel like for you?",
    ],
    "angry": [
        "I can hear how frustrated you are, and that makes complete sense. What happened?",
        "That kind of betrayal hurts deeply. I am here if you want to talk it through.",
        "Your anger sounds completely valid. What is going on?",
    ],
    "happy": [
        "That is wonderful! You deserve this. Tell me more about what happened!",
        "I love hearing this! What made this moment so special for you?",
        "That is amazing. You should be really proud. How are you feeling about it?",
    ],
    "neutral": [
        "I am here with you. Tell me more about what is on your mind.",
        "I am listening. What would you like to talk about today?",
        "Tell me more. I want to understand what you are going through.",
    ],
}

GREETINGS = [
    "Hey! I am VYNERA, your companion. I am here to listen and support you. What is on your mind today?",
    "Hi there! I am here for you. How are you feeling today?",
    "Hello! It is good to hear from you. What would you like to talk about?",
]

def _tok(text):
    return [w for w in re.sub(r"[^a-z\s]"," ",text.lower()).split() if len(w)>1]

def detect_emotion(text):
    words = set(text.lower().split())
    scores = {e: len(words & kws) for e, kws in EMOTION_WORDS.items()}
    if not any(scores.values()): return "neutral"
    return max(scores, key=scores.get)

def is_greeting(text):
    greet = {"hi","hello","hey","howdy","sup","yo","hiya",
             "how are you","how r u","good morning","good afternoon","good evening"}
    return text.lower().strip().rstrip("!?.") in greet or len(text.split()) <= 2

class VyneraRetriever:
    def __init__(self, index_path):
        with open(index_path, "rb") as f:
            data = pickle.load(f)
        self.vectors = data["vectors"]
        self.idf     = data["idf"]
        self.pairs   = data["pairs"]

    def retrieve(self, query, top_k=5):
        q_toks = _tok(query)
        if not q_toks: return []
        tf = Counter(q_toks)
        q_vec = {t: (tf[t]/len(q_toks))*self.idf.get(t,0) for t in tf}
        norm = math.sqrt(sum(v**2 for v in q_vec.values())) or 1
        q_vec = {t: v/norm for t,v in q_vec.items()}
        scores = [(sum(q_vec.get(t,0)*self.vectors[i].get(t,0) for t in q_vec), i)
                  for i in range(len(self.vectors))]
        scores.sort(reverse=True)
        return [(self.pairs[i]["context"], self.pairs[i]["response"], s)
                for s,i in scores[:top_k]]

    def get_response(self, user_text, conversation_history=None):
        user_text = user_text.strip()
        if is_greeting(user_text): return random.choice(GREETINGS)
        emotion = detect_emotion(user_text)
        query = user_text
        if conversation_history:
            last = next((m["content"] for m in reversed(conversation_history)
                        if m["role"]=="user"), "")
            if last and last != user_text: query = last + " " + user_text
        results = self.retrieve(query, top_k=5)
        good = [(c,r,s) for c,r,s in results if s >= 0.05]
        if good: return random.choice(good[:3])[1]
        return random.choice(FALLBACKS.get(emotion, FALLBACKS["neutral"]))
