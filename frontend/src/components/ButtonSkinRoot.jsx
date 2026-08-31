// Every button/tile/tab across the app always renders with the single wool
// felt look (icons/2-4.jpg reference) defined in index.css — previously this
// re-rolled one of four unrelated "materials" on every screen navigation,
// which read as the UI randomly breaking rather than a deliberate style.
export default function ButtonSkinRoot({ children }) {
  return <div className="app-shell">{children}</div>;
}
