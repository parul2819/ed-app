import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";
import * as api from "../api";
import * as storage from "../storage";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [parentToken, setParentToken] = useState(() => storage.getParentToken());
  const [cachedChildren, setCachedChildren] = useState([]);
  const [childrenLoading, setChildrenLoading] = useState(false);
  const [activeChild, setActiveChildState] = useState(() => storage.getActiveChild());

  const refreshChildren = useCallback(async () => {
    if (!parentToken) {
      setCachedChildren([]);
      return;
    }
    setChildrenLoading(true);
    try {
      const list = await api.listChildren(parentToken);
      setCachedChildren(list);
    } catch {
      setCachedChildren([]);
    } finally {
      setChildrenLoading(false);
    }
  }, [parentToken]);

  useEffect(() => {
    refreshChildren();
  }, [refreshChildren]);

  const signupParent = useCallback(async (email, password) => {
    const { access_token } = await api.signupParent(email, password);
    storage.setParentSession(access_token, email);
    setParentToken(access_token);
    return access_token;
  }, []);

  const loginParent = useCallback(async (email, password) => {
    const { access_token } = await api.loginParent(email, password);
    storage.setParentSession(access_token, email);
    setParentToken(access_token);
    return access_token;
  }, []);

  const logoutParent = useCallback(() => {
    storage.clearParentSession();
    setParentToken(null);
    setCachedChildren([]);
  }, []);

  const addChild = useCallback(
    async (name, pin, grade) => {
      const child = await api.addChild(parentToken, { name, pin, grade });
      await refreshChildren();
      return child;
    },
    [parentToken, refreshChildren]
  );

  const loginChildWithPin = useCallback(async (childId, pin) => {
    const session = await api.verifyChildPin(childId, pin);
    const child = { id: session.child_id, name: session.name, token: session.access_token };
    storage.setActiveChild(child);
    setActiveChildState(child);
    return child;
  }, []);

  const logoutChild = useCallback(() => {
    storage.clearActiveChild();
    setActiveChildState(null);
  }, []);

  const signOut = useCallback(() => {
    storage.clearActiveChild();
    storage.clearParentSession();
    setActiveChildState(null);
    setParentToken(null);
    setCachedChildren([]);
  }, []);

  const value = useMemo(
    () => ({
      parentToken,
      isParentLoggedIn: Boolean(parentToken),
      cachedChildren,
      childrenLoading,
      activeChild,
      signupParent,
      loginParent,
      logoutParent,
      addChild,
      loginChildWithPin,
      logoutChild,
      signOut,
    }),
    [
      parentToken,
      cachedChildren,
      childrenLoading,
      activeChild,
      signupParent,
      loginParent,
      logoutParent,
      addChild,
      loginChildWithPin,
      logoutChild,
      signOut,
    ]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within an AuthProvider");
  return ctx;
}
