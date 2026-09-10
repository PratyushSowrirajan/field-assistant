import { FormEvent, useState } from "react";
import { useTranslation } from "react-i18next";
import { Link, Navigate, useNavigate } from "react-router-dom";
import LanguageSwitcher from "@/components/LanguageSwitcher";
import { useAuth } from "@/hooks/useAuth";

export default function LoginPage() {
  const { login, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const { t } = useTranslation();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  if (isAuthenticated) return <Navigate to="/" replace />;

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await login(email, password);
      navigate("/");
    } catch {
      setError(t("auth.incorrectCredentials"));
    } finally {
      setLoading(false);
    }
  }

  return (
    <AuthShell title={t("auth.welcomeBack")} subtitle={t("auth.welcomeBackSubtitle")}>
      <form onSubmit={handleSubmit} className="space-y-4">
        <Field label={t("auth.email")}>
          <input
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="input"
            placeholder="you@farm.com"
          />
        </Field>
        <Field label={t("auth.password")}>
          <input
            type="password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="input"
            placeholder="••••••••"
          />
        </Field>
        {error && <p className="text-sm text-risk-critical">{error}</p>}
        <button type="submit" disabled={loading} className="btn-primary w-full">
          {loading ? t("auth.signingIn") : t("auth.signIn")}
        </button>
      </form>
      <p className="mt-6 text-center text-sm text-ink/70">
        {t("auth.newHere")}{" "}
        <Link to="/register" className="font-semibold text-forest hover:underline">
          {t("auth.createAccountLink")}
        </Link>
      </p>
    </AuthShell>
  );
}

export function AuthShell({
  title,
  subtitle,
  children,
}: {
  title: string;
  subtitle: string;
  children: React.ReactNode;
}) {
  return (
    <div className="flex min-h-screen items-center justify-center bg-forest px-4">
      <div className="w-full max-w-md">
        <div className="mb-4 flex justify-end">
          <LanguageSwitcher />
        </div>
        <div className="mb-6 text-center">
          <div className="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-xl bg-leaf text-cream text-xl font-bold">
            SF
          </div>
          <h1 className="text-2xl font-bold text-cream">{title}</h1>
          <p className="mt-1 text-sm text-cream/70">{subtitle}</p>
        </div>
        <div className="rounded-xl2 bg-cream p-6 shadow-card sm:p-8">{children}</div>
      </div>
    </div>
  );
}

export function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <label className="block">
      <span className="mb-1 block text-sm font-medium text-ink/80">{label}</span>
      {children}
    </label>
  );
}
