import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import TopBar from "../components/TopBar";
import ScreenBackground from "../components/ScreenBackground";
import { useAuth } from "../context/AuthContext";
import { getPassages, getPassageProgress, apiErrorMessage } from "../api";

// Mirrors reading_levels.py's DIFFICULTY_BANDS: ranks 1-10 easy, 11-30 medium, 31-50 hard.
function difficultyTier(rank) {
  if (rank <= 10) return "easy";
  if (rank <= 30) return "medium";
  return "hard";
}

const TIERS = [
  { key: "easy", label: "Easy" },
  { key: "medium", label: "Medium" },
  { key: "hard", label: "Hard" },
];

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

  const passagesByTier = { easy: [], medium: [], hard: [] };
  for (const passage of passages) {
    passagesByTier[difficultyTier(passage.difficulty_rank)].push(passage);
  }

  return (
    <div className="app-frame app-frame-wide">
      <ScreenBackground />
      <TopBar title="Reading Comprehension" onBack={() => navigate("/subjects")} />
      <div className="screen">
        {loading && <div className="loading-spinner" />}
        {error && <div className="error-banner">{error}</div>}

        {!loading && !error && passages.length === 0 && (
          <p className="subtitle">No passages available yet — check back soon!</p>
        )}

        {!loading &&
          passages.length > 0 &&
          TIERS.map(({ key, label }) => {
            const tierPassages = passagesByTier[key];
            if (tierPassages.length === 0) return null;
            return (
              <section key={key} className="passage-category">
                <h2 className={`passage-category-heading passage-category-heading-${key}`}>
                  <span className={`difficulty-dot difficulty-dot-${key}`} /> {label}
                </h2>
                <div className="passage-grid">
                  {tierPassages.map((passage) => {
                    const completed = progressByPassage[passage.id];
                    return (
                      <button
                        key={passage.id}
                        type="button"
                        className="passage-grid-card"
                        onClick={() => navigate(`/english/passages/${passage.id}`)}
                      >
                        {completed && (
                          <span className="passage-grid-card-badge">
                            ✅ {completed.stars_earned > 0 ? "⭐".repeat(completed.stars_earned) : ""}
                          </span>
                        )}
                        <span className="passage-grid-card-level">Level {passage.difficulty_rank}</span>
                        <span className="passage-grid-card-title">{passage.title}</span>
                      </button>
                    );
                  })}
                </div>
              </section>
            );
          })}
      </div>
    </div>
  );
}
