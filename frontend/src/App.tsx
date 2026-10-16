import { useEffect, useState } from "react";
import "./App.css";
import { apiFetch, ApiError } from "./api/client";
import { SongConnection } from "./components/SongConnection";
import { useAuth } from "./context/AuthContext";
import type { Song } from "./components/SongSelector";

type Recommendation = Song & { connection_id: number; supporter_count: number };
type Supporter = { user_id: number; username: string; rank: number; points: number };
type History = { connection_id: number; song_1_id: number; song_2_id: number; created_at: string; points: number; supporter_count: number };

function useRoute() {
  const [path, setPath] = useState(window.location.pathname);
  useEffect(() => { const onPop = () => setPath(window.location.pathname); window.addEventListener("popstate", onPop); return () => window.removeEventListener("popstate", onPop); }, []);
  return { path, go: (next: string) => { window.history.pushState({}, "", next); setPath(next); } };
}

function Login({ signup = false }: { signup?: boolean }) {
  const { login } = useAuth();
  const [username, setUsername] = useState(""); const [password, setPassword] = useState(""); const [error, setError] = useState<string | null>(null);
  async function submit() { try { if (signup) await apiFetch("/auth/signup", { method: "POST", body: JSON.stringify({ username, password }) }); await login(username, password); window.location.href = "/"; } catch (err) { setError(err instanceof ApiError ? err.message : "Unable to authenticate"); } }
  return <section className="card"><h2>{signup ? "Create an account" : "Log in"}</h2><input placeholder="Username" value={username} onChange={e => setUsername(e.target.value)} /><input placeholder="Password" type="password" value={password} onChange={e => setPassword(e.target.value)} /><button onClick={submit}>{signup ? "Sign up" : "Log in"}</button>{error && <p className="error">{error}</p>}</section>;
}

function Discovery() {
  const [query, setQuery] = useState(""); const [songs, setSongs] = useState<Song[]>([]); const [selected, setSelected] = useState<Song | null>(null); const [recommendations, setRecommendations] = useState<Recommendation[]>([]); const [supporters, setSupporters] = useState<Supporter[]>([]); const [error, setError] = useState<string | null>(null);
  async function search() { try { setError(null); setSongs(await apiFetch<Song[]>(`/songs/search?title=${encodeURIComponent(query)}`)); } catch (err) { setError(err instanceof ApiError ? err.message : "Search failed"); } }
  async function choose(song: Song) { setSelected(song); setSongs([]); setRecommendations(await apiFetch<Recommendation[]>(`/songs/${song.id}/connections`)); }
  return <section className="card"><h2>Find similar songs</h2><div className="row"><input placeholder="Search by song title" value={query} onChange={e => setQuery(e.target.value)} /><button onClick={search}>Search</button></div>{error && <p className="error">{error}</p>}{!selected && songs.map(song => <button className="result" key={song.id} onClick={() => choose(song)}>{song.title} — {song.artist}</button>)}{selected && <><p><strong>{selected.title}</strong> — {selected.artist}</p><button onClick={() => { setSelected(null); setRecommendations([]); setSupporters([]); }}>Choose another</button><h3>Community connections</h3>{recommendations.length === 0 ? <p>No connections yet.</p> : recommendations.map(song => <div className="recommendation" key={song.connection_id}><button onClick={async () => setSupporters(await apiFetch<Supporter[]>(`/connections/${song.connection_id}/supporters`))}>{song.title} — {song.artist}</button><small>{song.supporter_count} supporter{song.supporter_count === 1 ? "" : "s"}</small></div>)}{supporters.length > 0 && <><h3>Supporters</h3>{supporters.map(s => <div className="recommendation" key={s.user_id}><span>#{s.rank} {s.username}</span><small>{s.points.toFixed(2)} points</small></div>)}</>}</>}</section>;
}

function HistoryView() {
  const [items, setItems] = useState<History[]>([]); const [songs, setSongs] = useState<Record<number, Song>>({}); const [error, setError] = useState<string | null>(null);
  useEffect(() => { apiFetch<History[]>("/connections/mine").then(async history => { setItems(history); const ids = [...new Set(history.flatMap(item => [item.song_1_id, item.song_2_id]))]; const entries = await Promise.all(ids.map(async id => [id, await apiFetch<Song>(`/songs/${id}`)] as const)); setSongs(Object.fromEntries(entries)); }).catch(err => setError(err instanceof ApiError ? err.message : "Unable to load history")); }, []);
  return <section className="card"><h2>My connections</h2>{error && <p className="error">{error}</p>}{items.length === 0 && !error && <p>You have not made any connections yet.</p>}{items.map(item => <div className="history" key={item.connection_id}><strong>{songs[item.song_1_id]?.title ?? "Song"} ↔ {songs[item.song_2_id]?.title ?? "Song"}</strong><span>{new Date(item.created_at).toLocaleString()} · {item.points.toFixed(2)} points · {item.supporter_count} supporters</span></div>)}</section>;
}

function App() {
  const { path, go } = useRoute(); const { isAuthenticated, user, logout } = useAuth();
  const view = path === "/login" ? <Login /> : path === "/signup" ? <Login signup /> : path === "/history" ? <HistoryView /> : path === "/discover" ? <Discovery /> : <SongConnection />;
  return <><header><button className="brand" onClick={() => go("/")}>Song Network</button><nav><button onClick={() => go("/discover")}>Discover</button>{isAuthenticated && <button onClick={() => go("/history")}>My connections</button>}{isAuthenticated ? <><span>{user?.username}</span><button onClick={logout}>Log out</button></> : <><button onClick={() => go("/login")}>Log in</button><button onClick={() => go("/signup")}>Sign up</button></>}</nav></header><main>{view}</main></>;
}

export default App;
