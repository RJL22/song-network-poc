import { useState } from "react";
import { apiFetch } from "../api/client";

export interface Song {
  id: number;
  mb_id: string;
  title: string;
  artist: string;
}

interface SongSelectorProps {
  selected: Song | null;
  onSelect: (song: Song) => void;
  onDeselect: () => void;
}

export function SongSelector({ selected, onSelect, onDeselect }: SongSelectorProps) {
  const [title, setTitle] = useState("");
  const [artist, setArtist] = useState("");
  const [results, setResults] = useState<Song[]>([]);

  async function handleSearch() {
    const params = new URLSearchParams({ title, artist });
    const data = await apiFetch(`/songs/search2?${params.toString()}`);
    setResults(data);
  }

  if (selected) {
    return (
      <div onClick={onDeselect} style={{ cursor: "pointer" }}>
        <strong>{selected.title}</strong> — {selected.artist}
        <span style={{ marginLeft: 8, fontSize: "0.85em", color: "#666" }}>
          (click to change)
        </span>
      </div>
    );
  }

  return (
    <div>
      <input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Song title" />
      <input value={artist} onChange={(e) => setArtist(e.target.value)} placeholder="Artist" />
      <button onClick={handleSearch}>Search</button>
      <ul>
        {results.map((song) => (
          <li key={song.id} onClick={() => onSelect(song)} style={{ cursor: "pointer" }}>
            {song.title} — {song.artist}
          </li>
        ))}
      </ul>
    </div>
  );
}