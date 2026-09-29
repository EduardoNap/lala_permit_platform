"""Página de inicio de sesión."""

from __future__ import annotations

import reflex as rx

from ..state import State


def auth_field(
    label: str,
    placeholder: str,
    value: rx.Var,
    on_change: rx.EventHandler,
    field_type: str = "text",
) -> rx.Component:
    return rx.vstack(
        rx.text(label, class_name="login-label"),
        rx.input(
            type=field_type,
            placeholder=placeholder,
            value=value,
            on_change=on_change,
            class_name="login-input",
        ),
        class_name="login-field",
        width="100%",
    )


def login_card() -> rx.Component:
    return rx.box(
        rx.el.style(
            """
            .login-layout {
              min-height: 100vh;
              width: 100%;
              display: flex;
              background: #f1f5f9;
              font-family: "Space Grotesk", "IBM Plex Sans", sans-serif;
            }
            .login-left {
              flex: 1;
              background: #ffffff;
              padding: 72px 84px;
              display: flex;
              flex-direction: column;
              gap: 28px;
              position: relative;
              justify-content: center;
              align-items: center;
            }
            .login-left-content {
              width: 100%;
              max-width: 460px;
            }
            .login-right {
              flex: 1;
              background: #f5f6fb;
              display: flex;
              align-items: center;
              justify-content: center;
              position: relative;
              overflow: hidden;
            }
            .login-brand {
              color: #0f172a;
              font-weight: 600;
              font-size: 13px;
            }
            .login-title {
              font-size: 30px;
              font-weight: 600;
              color: #0f172a;
            }
            .login-subtitle {
              font-size: 13px;
              color: #64748b;
            }
            .login-field {
              gap: 6px;
            }
            .login-label {
              font-size: 11px;
              letter-spacing: 0.08em;
              text-transform: uppercase;
              color: #94a3b8;
              font-weight: 600;
            }
            .login-input {
              border: 1px solid #e5e7eb;
              border-radius: 10px;
              padding: 10px 12px;
              font-size: 13px;
              color: #0f172a;
              background: #ffffff;
            }
            .login-input:focus {
              outline: none;
              border-color: #7c3aed;
              box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.15);
            }
            .login-primary {
              background: #7c3aed;
              color: white;
              border: none;
              font-weight: 600;
              border-radius: 10px;
              box-shadow: 0 14px 28px rgba(124, 58, 237, 0.25);
            }
            .login-link {
              color: #7c3aed;
              font-weight: 600;
            }
            .login-footer {
              position: absolute;
              left: 28px;
              bottom: 20px;
              font-size: 12px;
              color: #94a3b8;
            }
            .login-orb {
              width: 240px;
              height: 240px;
              border-radius: 999px;
              background: radial-gradient(circle at 30% 30%, #a78bfa 0%, #7c3aed 45%, #5b21b6 100%);
              box-shadow: 0 30px 70px rgba(76, 29, 149, 0.35);
              position: relative;
              z-index: 2;
            }
            .login-orb-shadow {
              position: absolute;
              width: 280px;
              height: 50px;
              border-radius: 999px;
              background: radial-gradient(circle, rgba(124, 58, 237, 0.45) 0%, rgba(124, 58, 237, 0.12) 60%, rgba(124, 58, 237, 0) 100%);
              filter: blur(8px);
              transform: translateY(90px);
              z-index: 1;
            }
            @media (max-width: 900px) {
              .login-layout { flex-direction: column; }
              .login-left { padding: 56px 28px 80px; }
              .login-right { min-height: 240px; }
            }
            """
        ),
        rx.box(
            rx.box(
                rx.vstack(
                    rx.hstack(
                        rx.box(
                            width="8px",
                            height="8px",
                            border_radius="999px",
                            background="#0f172a",
                        ),
                        rx.text("Frogh Platform", class_name="login-brand"),
                        spacing="2",
                        align="center",
                    ),
                    rx.vstack(
                        rx.text(
                            rx.cond(
                                State.auth_mode == "register",
                                "Crea tu cuenta",
                                "Bienvenido de nuevo",
                            ),
                            class_name="login-title",
                        ),
                        rx.text(
                            rx.cond(
                                State.auth_mode == "register",
                                rx.cond(
                                    State.has_users,
                                    "Crea un usuario nuevo para continuar.",
                                    "Primera vez: crea tu usuario administrador.",
                                ),
                                "Ingresa tus datos para continuar.",
                            ),
                            class_name="login-subtitle",
                        ),
                        spacing="1",
                        align="start",
                    ),
                    rx.vstack(
                        auth_field(
                            "Usuario",
                            "Ingresa tu usuario",
                            State.auth_username,
                            State.set_auth_username,
                        ),
                        rx.cond(
                            State.auth_mode == "register",
                            auth_field(
                                "Correo",
                                "Ingresa tu correo",
                                State.auth_email,
                                State.set_auth_email,
                                field_type="email",
                            ),
                            rx.box(),
                        ),
                        auth_field(
                            "Contraseña",
                            "Ingresa tu contraseña",
                            State.auth_password,
                            State.set_auth_password,
                            field_type="password",
                        ),
                        rx.cond(
                            State.auth_mode == "register",
                            auth_field(
                                "Nombre visible",
                                "Nombre para mostrar",
                                State.auth_display_name,
                                State.set_auth_display_name,
                            ),
                            rx.box(),
                        ),
                        spacing="3",
                        width="100%",
                    ),
                    rx.button(
                        rx.cond(
                            State.auth_mode == "register",
                            "Crear cuenta",
                            "Iniciar sesión",
                        ),
                        size="2",
                        width="100%",
                        on_click=State.submit_auth,
                        class_name="login-primary",
                    ),
                    rx.cond(
                        State.has_users,
                        rx.hstack(
                            rx.text(
                                rx.cond(
                                    State.auth_mode == "register",
                                    "¿Ya tienes cuenta?",
                                    "¿No tienes cuenta?",
                                ),
                                font_size="12px",
                                color="#64748b",
                            ),
                            rx.button(
                                rx.cond(
                                    State.auth_mode == "register",
                                    "Inicia sesión",
                                    "Regístrate",
                                ),
                                size="1",
                                variant="ghost",
                                on_click=rx.cond(
                                    State.auth_mode == "register",
                                    State.set_auth_mode_login,
                                    State.set_auth_mode_register,
                                ),
                                class_name="login-link",
                            ),
                            spacing="2",
                            align="center",
                        ),
                        rx.box(),
                    ),
                    rx.cond(
                        State.auth_error != "",
                        rx.text(
                            State.auth_error,
                            font_size="12px",
                            color="#dc2626",
                        ),
                        rx.cond(
                            State.auth_info != "",
                            rx.text(
                                State.auth_info,
                                font_size="12px",
                                color="#2563eb",
                            ),
                            rx.box(),
                        ),
                    ),
                    spacing="3",
                    width="100%",
                    align="start",
                ),
                class_name="login-left-content",
            ),
            rx.text("Frogh Plataform \u00a9", class_name="login-footer"),
            class_name="login-left",
        ),
        rx.box(
            rx.box(class_name="login-orb"),
            rx.box(class_name="login-orb-shadow"),
            class_name="login-right",
        ),
        class_name="login-layout",
        width="100%",
    )


def login_page() -> rx.Component:
    return rx.box(login_card(), width="100%")
