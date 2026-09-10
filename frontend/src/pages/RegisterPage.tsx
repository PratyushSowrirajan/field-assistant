import { FormEvent, useState } from "react";
import { useTranslation } from "react-i18next";
import { Link, Navigate, useNavigate } from "react-router-dom";
import { useAuth } from "@/hooks/useAuth";
import { AuthShell, Field } from "./LoginPage";

export default function RegisterPage() {
  const { register, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const { t } = useTranslation();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  if (isAuthenticated) return <Navigate to="/" replace />;

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await register(name, email, password, phone || undefined);
      navigate("/");
    } catch (err: any) {
      setError(err?.response?.data?.detail || t("auth.couldNotCreateAccount"));
    } finally {
      setLoading(false);
    }
  }

  return (
    <AuthShell title={t("auth.createYourAccount")} subtitle={t("auth.createAccountSubtitle")}>
      <form onSubmit={handleSubmit} className="space-y-4">
        <Field label={t("auth.fullName")}>
          <input required value={name} onChange={(e) => setName(e.target.value)} className="input" />
        </Field>
        <Field label={t("auth.email")}>
          <input
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="input"
          />
        </Field>
        <Field label={t("auth.phoneOptional")}>
          <input value={phone} onChange={(e) => setPhone(e.target.value)} className="input" />
        </Field>
        <Field label={t("auth.password")}>
          <input
            type="password"
            required
            minLength={8}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="input"
          />
        </Field>
        {error && <p className="text-sm text-risk-critical">{error}</p>}
        <button type="submit" disabled={loading} className="btn-primary w-full">
          {loading ? t("auth.creatingAccount") : t("auth.createAccount")}
        </button>
      </form>
      <p className="mt-6 text-center text-sm text-ink/70">
        {t("auth.alreadyHaveAccount")}{" "}
        <Link to="/login" className="font-semibold text-forest hover:underline">
          {t("auth.signIn")}
        </Link>
      </p>
    </AuthShell>
  );
}
