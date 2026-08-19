import { useState } from "react";
import { SongSelector, type Song } from "./SongSelector";
import { apiFetch, ApiError } from "../api/client";

export function SongConnection() {
  const [songA, setSongA] = useState<Song | null>(null);
  const [songB, setSongB] = useState<Song | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [status, setStatus] = useState<string | null>(null);

  async function handleConnect() {
    if (!songA || !songB) return;
    setError(null);
    setStatus(null);
    try {
      await apiFetch("/connections", {
        method: "POST",
        body: JSON.stringify({
          song_1_id: songA.id,
          song_2_id: songB.id,
        }),
      });
      setStatus("Connection created!");
      setSongA(null);
      setSongB(null);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to create connection.");
    }
  }

  return (
    <div>
      <h2>Connect two songs</h2>

      <SongSelector selected={songA} onSelect={setSongA} onDeselect={() => setSongA(null)} />
      <SongSelector selected={songB} onSelect={setSongB} onDeselect={() => setSongB(null)} />

      <button onClick={handleConnect} disabled={!songA || !songB}>
        Connect
      </button>

      {error && <p style={{ color: "red" }}>{error}</p>}
      {status && <p style={{ color: "green" }}>{status}</p>}
    </div>
  );
}