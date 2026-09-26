from app import create_app
from app.models import db, User, Project, ProjectFile, ProjectIssue, IssueComment, Post, PostComment, Activity

def seed_database():
    app = create_app()
    with app.app_context():
        db.create_all()

        if User.query.first():
            print("Database already contains data. Skipping seeding.")
            return

        print("Seeding initial developer profiles, repositories, and social posts...")

        # 1. Create Sample Users
        u1 = User(
            username="alex_dev",
            email="alex@devhub.local",
            display_name="Alex Rivers",
            title="Senior Backend & Distributed Systems",
            bio="Building high-performance distributed backends, CLI tools, and exploring Python & Go. Open source contributor.",
            location="San Francisco, CA",
            website="https://alexrivers.dev",
            github_username="alexrivers",
            twitter_username="alexrivers_dev",
            skills="Python, Go, Docker, PostgreSQL, Redis, Kubernetes"
        )
        u1.set_password("password123")

        u2 = User(
            username="sarah_ai",
            email="sarah@devhub.local",
            display_name="Sarah Chen",
            title="Machine Learning Engineer & Researcher",
            bio="Working on vector databases, multimodal LLMs, and open-source generative AI toolkits.",
            location="Seattle, WA",
            website="https://sarahchen.ai",
            github_username="sarahchen",
            twitter_username="sarahchen_ai",
            skills="Python, PyTorch, Transformers, LangChain, CUDA, FastAPI"
        )
        u2.set_password("password123")

        u3 = User(
            username="marcus_rust",
            email="marcus@devhub.local",
            display_name="Marcus Vance",
            title="Systems & Infrastructure Engineer",
            bio="Writing safe and concurrent systems in Rust. Enthusiast of WebAssembly and low-latency networking.",
            location="Berlin, Germany",
            github_username="marcusvance",
            skills="Rust, WebAssembly, C++, Linux, Tokio, Raft"
        )
        u3.set_password("password123")

        u4 = User(
            username="elena_ui",
            email="elena@devhub.local",
            display_name="Elena Gomez",
            title="Frontend Architect & UI Enthusiast",
            bio="Obsessed with micro-interactions, accessibility, modern CSS, and lightweight reactive frontends.",
            location="Barcelona, Spain",
            github_username="elenagomez",
            skills="TypeScript, React, TailwindCSS, Next.js, HTML5, WebGL"
        )
        u4.set_password("password123")

        db.session.add_all([u1, u2, u3, u4])
        db.session.commit()

        # Follow relationships
        u1.follow(u2)
        u1.follow(u3)
        u2.follow(u1)
        u2.follow(u4)
        u3.follow(u1)
        u4.follow(u1)
        u4.follow(u2)
        db.session.commit()

        # 2. Create Repositories / Projects

        # Project 1: neural-search-engine
        p1 = Project(
            user_id=u2.id,
            name="neural-search-engine",
            tagline="Hybrid vector & keyword semantic search engine with BM25 reranking",
            description="A lightweight, self-contained semantic search library that combines dense vector embeddings with BM25 keyword relevance.",
            primary_language="Python",
            topics="search, machine-learning, embeddings, python, nlp",
            license="MIT",
            github_url="https://github.com/sarahchen/neural-search-engine",
            demo_url="https://neural-search-demo.local",
            is_pinned=True,
            is_public=True,
            stars_count=18,
            readme_content="""# Neural Search Engine 🧠🔍

A production-ready hybrid search engine combining sparse BM25 retrieval with dense vector cosine similarity.

## Features
- **Hybrid Retrieval**: Combines exact lexical matching with semantic understanding.
- **Fast In-Memory Index**: Optimized numpy-accelerated dot product calculations.
- **Pluggable Tokenizers**: Compatible with SentencePiece, Byte-Pair Encoding, and regex word splitters.

## Quickstart

```python
from search import NeuralSearch

# Initialize search engine
engine = NeuralSearch(dim=384)

# Index documents
engine.add_document(id=1, text="Fast distributed systems in Rust")
engine.add_document(id=2, text="Machine learning model serving in Python")

# Query
results = engine.search("How to build concurrent backends?", top_k=5)
for res in results:
    print(f"[{res.score:.2f}] {res.text}")
```

## License
MIT License. Free for commercial and private use.
"""
        )
        db.session.add(p1)
        db.session.commit()

        # Add files to p1
        f1_1 = ProjectFile(
            project_id=p1.id,
            filename="README.md",
            content=p1.readme_content,
            file_size=len(p1.readme_content.encode('utf-8')),
            language="markdown"
        )
        f1_2 = ProjectFile(
            project_id=p1.id,
            filename="search.py",
            content="""import math
from typing import List, Dict, Any

class NeuralSearch:
    def __init__(self, dim: int = 384, alpha: float = 0.5):
        self.dim = dim
        self.alpha = alpha  # Weight between dense & sparse scores
        self.documents: Dict[int, str] = {}
        self.vectors: Dict[int, List[float]] = {}

    def add_document(self, id: int, text: str, vector: List[float] = None) -> None:
        self.documents[id] = text
        if vector is not None:
            self.vectors[id] = self._normalize(vector)

    def _normalize(self, vec: List[float]) -> List[float]:
        norm = math.sqrt(sum(x * x for x in vec)) or 1.0
        return [x / norm for x in vec]

    def cosine_similarity(self, a: List[float], b: List[float]) -> float:
        return sum(x * y for x, y in zip(a, b))

    def search(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        # Hybrid ranking logic
        results = []
        for doc_id, text in self.documents.items():
            results.append({
                "id": doc_id,
                "text": text,
                "score": 0.94
            })
        return results[:top_k]
""",
            file_size=1024,
            language="python"
        )
        db.session.add_all([f1_1, f1_2])

        # Project 2: rusty-kv-store
        p2 = Project(
            user_id=u3.id,
            name="rusty-kv",
            tagline="Embedded persistent key-value store with LSM-tree storage and WAL",
            description="Ultra-fast embedded key-value storage engine built in Rust with Write-Ahead Logging (WAL) and memory-mapped SSTables.",
            primary_language="Rust",
            topics="rust, database, kv-store, storage-engine, lsm-tree",
            license="Apache-2.0",
            github_url="https://github.com/marcusvance/rusty-kv",
            is_pinned=True,
            is_public=True,
            stars_count=24,
            readme_content="""# RustyKV 🦀⚡

An asynchronous, thread-safe embedded key-value database engine written in Rust.

## Architecture Highlights
- **MemTable**: Concurrent SkipList in RAM for O(log N) zero-lock concurrent reads and writes.
- **WAL (Write Ahead Log)**: Sequential fsync guarantees crash-resilience with zero data corruption.
- **SSTables**: Immutable on-disk sorted string tables with Bloom filters for single-seek key lookups.

## Example Usage

```rust
use rusty_kv::Store;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let mut store = Store::open("./data")?;

    store.set("user:101", "Alex Rivers")?;
    if let Some(val) = store.get("user:101")? {
        println!("Found user: {}", val);
    }
    Ok(())
}
```
"""
        )
        db.session.add(p2)
        db.session.commit()

        f2_1 = ProjectFile(
            project_id=p2.id,
            filename="README.md",
            content=p2.readme_content,
            file_size=len(p2.readme_content.encode('utf-8')),
            language="markdown"
        )
        f2_2 = ProjectFile(
            project_id=p2.id,
            filename="src/main.rs",
            content="""use std::collections::BTreeMap;
use std::sync::RwLock;

pub struct MemTable {
    map: RwLock<BTreeMap<String, Vec<u8>>>,
}

impl MemTable {
    pub fn new() -> Self {
        Self {
            map: RwLock::new(BTreeMap::new()),
        }
    }

    pub fn insert(&self, key: String, value: Vec<u8>) {
        let mut writer = self.map.write().unwrap();
        writer.insert(key, value);
    }

    pub fn get(&self, key: &str) -> Option<Vec<u8>> {
        let reader = self.map.read().unwrap();
        reader.get(key).cloned()
    }
}

fn main() {
    let memtable = MemTable::new();
    memtable.insert("cluster_id".to_string(), b"us-east-4".to_vec());
    println!("RustyKV Initialized successfully!");
}
""",
            file_size=750,
            language="rust"
        )
        db.session.add_all([f2_1, f2_2])

        # Project 3: micro-router-js
        p3 = Project(
            user_id=u4.id,
            name="micro-router",
            tagline="Zero-dependency client-side SPA router under 1KB with View Transitions support",
            description="Tiny, blazing-fast single page application router supporting HTML5 History API, dynamic param extraction, and native View Transitions API.",
            primary_language="JavaScript",
            topics="javascript, router, spa, webdev, micro-library",
            license="MIT",
            demo_url="https://micro-router.demo",
            is_pinned=True,
            is_public=True,
            stars_count=12,
            readme_content="""# Micro Router 🚀

Minimalist client-side routing library under **850 bytes** gzipped.

## Why Micro Router?
- 0 dependencies
- First-class support for `document.startViewTransition()`
- Regex-compiled path matchers (`/users/:id/edit`)

```javascript
import { Router } from 'micro-router';

const router = new Router();

router.on('/feed', () => renderFeed());
router.on('/projects/:id', ({ id }) => renderProject(id));
router.resolve();
```
"""
        )
        db.session.add(p3)
        db.session.commit()

        f3_1 = ProjectFile(
            project_id=p3.id,
            filename="README.md",
            content=p3.readme_content,
            file_size=len(p3.readme_content.encode('utf-8')),
            language="markdown"
        )
        f3_2 = ProjectFile(
            project_id=p3.id,
            filename="index.js",
            content=r"""export class Router {
  constructor() {
    this.routes = [];
    window.addEventListener('popstate', () => this.resolve());
  }

  on(pattern, handler) {
    const regex = new RegExp('^' + pattern.replace(/:([^\/]+)/g, '(?<$1>[^\/]+)') + '$');
    this.routes.push({ regex, handler });
    return this;
  }

  navigate(url) {
    history.pushState(null, '', url);
    this.resolve();
  }

  resolve() {
    const path = window.location.pathname;
    for (const route of this.routes) {
      const match = path.match(route.regex);
      if (match) {
        if (document.startViewTransition) {
          document.startViewTransition(() => route.handler(match.groups || {}));
        } else {
          route.handler(match.groups || {});
        }
        return;
      }
    }
  }
}
""",
            file_size=820,
            language="javascript"
        )
        db.session.add_all([f3_1, f3_2])

        # Project 4: secure-auth-gateway
        p4 = Project(
            user_id=u1.id,
            name="secure-auth-gateway",
            tagline="Hardened authentication & token verification microservice with Scrypt & Rate Limiting",
            description="Self-hosted security proxy offering session management, brute-force mitigation, and CSRF token generation.",
            primary_language="Python",
            topics="security, python, authentication, cryptography, api",
            license="MIT",
            is_pinned=True,
            is_public=True,
            stars_count=31,
            readme_content="""# Secure Auth Gateway 🛡️

A hardened local-first authentication microservice.

## Security Controls
- **Memory-Hard Hashing**: Scrypt password derivation (N=32768, r=8, p=1).
- **Rate-Limiting**: IP-based token bucket protecting login endpoints.
- **Tamper-Proof Cookies**: SameSite=Lax + HttpOnly with AES-GCM signed sessions.
"""
        )
        db.session.add(p4)
        db.session.commit()

        # Stars
        u1.star_project(p1)
        u1.star_project(p2)
        u2.star_project(p2)
        u2.star_project(p4)
        u3.star_project(p1)
        u3.star_project(p4)
        u4.star_project(p1)
        u4.star_project(p3)
        u4.star_project(p4)
        db.session.commit()

        # 3. Create Sample Issues
        issue1 = ProjectIssue(
            project_id=p1.id,
            user_id=u1.id,
            title="Feature: Support batch vector queries for high-throughput pipelines",
            body="When running indexing over 100k items, single-vector cosine similarity becomes a memory bottleneck. We should accept a 2D numpy matrix and compute batched matrix-vector dot products via BLAS.",
            label="enhancement",
            status="open"
        )
        db.session.add(issue1)
        db.session.commit()

        comment1 = IssueComment(
            issue_id=issue1.id,
            user_id=u2.id,
            body="Great suggestion Alex! I am benchmarking `scipy.spatial.distance.cdist` vs pure vectorized numpy right now. Will open a PR this weekend."
        )
        db.session.add(comment1)

        issue2 = ProjectIssue(
            project_id=p2.id,
            user_id=u1.id,
            title="Add auto-compaction trigger when tombstone count exceeds 30%",
            body="Under heavy delete workloads, old SSTables linger with dead keys. A background compaction thread will keep read latency low.",
            label="enhancement",
            status="open"
        )
        db.session.add(issue2)
        db.session.commit()

        # 4. Create Social Feed Posts
        post1 = Post(
            user_id=u2.id,
            content="🚀 Just open-sourced **neural-search-engine**! It combines dense vector retrieval with classic BM25 keyword reranking. Here's a quick preview of how simple the indexing API is:",
            code_snippet="""from search import NeuralSearch

engine = NeuralSearch(dim=384)
engine.add_document(1, "Fast distributed systems in Rust")
results = engine.search("low latency concurrency")
print(results)""",
            code_language="python",
            project_id=p1.id,
            likes_count=14,
            comments_count=2
        )
        db.session.add(post1)
        db.session.commit()

        c1 = PostComment(
            post_id=post1.id,
            user_id=u1.id,
            content="Awesome project Sarah! The hybrid scoring is definitely the sweet spot for search accuracy."
        )
        c2 = PostComment(
            post_id=post1.id,
            user_id=u3.id,
            content="Really clean implementation. I wonder if we could port the vector matrix multiplications to Rust via PyO3 for a 5x speedup!"
        )
        db.session.add_all([c1, c2])

        post2 = Post(
            user_id=u3.id,
            content="Quick tip for Rust concurrency: If you have read-heavy workloads with rare mutations, prefer `parking_lot::RwLock` over standard library mutexes. In high-contention benchmarks, we saw a **3.8x throughput improvement** in RustyKV.",
            code_snippet="""use parking_lot::RwLock;
use std::sync::Arc;

struct Cache {
    data: Arc<RwLock<Vec<u8>>>,
}

impl Cache {
    fn read_fast(&self) -> usize {
        let lock = self.data.read();
        lock.len()
    }
}""",
            code_language="rust",
            project_id=p2.id,
            likes_count=21,
            comments_count=1
        )
        db.session.add(post2)
        db.session.commit()

        c3 = PostComment(
            post_id=post2.id,
            user_id=u1.id,
            content="`parking_lot` is amazing. The spin-lock fallback under microsecond waits completely eliminates kernel context switches."
        )
        db.session.add(c3)

        post3 = Post(
            user_id=u4.id,
            content="The native browser **View Transitions API** is fundamentally changing how web apps feel. You no longer need heavy animation libraries just to get smooth cross-fade route morphing! ✨",
            code_snippet="""// In pure modern JavaScript:
document.startViewTransition(() => {
  updateDOMForNextPage();
});""",
            code_language="javascript",
            project_id=p3.id,
            likes_count=9,
            comments_count=0
        )
        db.session.add(post3)

        post4 = Post(
            user_id=u1.id,
            content="Security PSA for anyone designing local PC applications:\n\n1. Always bind to `127.0.0.1` (loopback) rather than `0.0.0.0` unless external access is explicitly requested.\n2. Store secrets in memory or local salted hashes rather than plaintext config files.\n3. Validate `os.path.commonpath` to eliminate directory traversal risks completely.\n\nBuilding DevHub with these exact principles!",
            likes_count=19,
            comments_count=1
        )
        db.session.add(post4)
        db.session.commit()

        # Likes on posts
        u1.like_post(post1)
        u1.like_post(post2)
        u2.like_post(post2)
        u2.like_post(post4)
        u3.like_post(post1)
        u4.like_post(post1)
        u4.like_post(post4)

        # Bookmarks
        u1.toggle_bookmark(post2)
        u1.toggle_bookmark(post3)

        # Activities
        a1 = Activity(user_id=u2.id, activity_type='project_created', description="Published neural-search-engine", link=f"/projects/{p1.id}")
        a2 = Activity(user_id=u3.id, activity_type='project_created', description="Published rusty-kv", link=f"/projects/{p2.id}")
        a3 = Activity(user_id=u4.id, activity_type='project_created', description="Published micro-router", link=f"/projects/{p3.id}")
        a4 = Activity(user_id=u1.id, activity_type='project_created', description="Published secure-auth-gateway", link=f"/projects/{p4.id}")
        db.session.add_all([a1, a2, a3, a4])

        db.session.commit()
        print("Initial database seeded successfully!")

if __name__ == '__main__':
    seed_database()
