import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import TopBar from "../components/TopBar";
import ScreenBackground from "../components/ScreenBackground";
import { useAuth } from "../context/AuthContext";
import { getPassages, getPassageProgress, apiErrorMessage } from "../api";

export default function PassageListPage() {
  const navigate = useNavigate();
  const { activeChild } = useAuth();
  const [passages, setPassages] = useState([]);
  const [progressByPassage, setProgressByPassage] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;
    (async () => {
      setLoading(true);
      setError("");
      try {
        const data = await getPassages();
        if (!cancelled) setPassages(data);
      } catch (err) {
        if (!cancelled) setError(apiErrorMessage(err, "Couldn't load passages."));
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const rows = await getPassageProgress(activeChild.token, activeChild.id);
        if (cancelled) return;
        const byPassage = {};
        for (const row of rows) byPassage[row.passage_id] = row;
        setProgressByPassage(byPassage);
      } catch {
        // Completion badges are a nice-to-have — the list still works without them.
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [activeChild]);

  return (
    <div className="app-frame">
      <ScreenBackground />
      <TopBar title="Reading Comprehension" onBack={() => navigate("/subjects")} />
      <div className="screen">
        {loading && <div className="loading-spinner" />}
        {error && <div className="error-banner">{error}</div>}

        {!loading && !error && passages.length === 0 && (
          <p className="subtitle">No passages available yet — check back soon!</p>
        )}

        {!loading && passages.length > 0 && (
          <div className="passage-list">
            {passages.map((passage) => {
              const completed = progressByPassage[passage.id];
              return (
                <button
                  key={passage.id}
                  type="button"
                  className="passage-card"
                  onClick={() => navigate(`/english/passages/${passage.id}`)}
                >
                  <div className="passage-card-title-row">
                    <span className="passage-card-title">{passage.title}</span>
                    {completed && (
                      <span className="passage-card-badge">
                        ✅ {completed.stars_earned > 0 ? "⭐".repeat(completed.stars_earned) : ""}
                      </span>
                    )}
                  </div>
                  <span className="passage-card-meta">
                    Level {passage.difficulty_rank} · {passage.word_count} words
                  </span>
                </button>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
