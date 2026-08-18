(function () {
    const $ = (selector, root = document) => root.querySelector(selector);
    const $$ = (selector, root = document) => Array.from(root.querySelectorAll(selector));

    function clamp(value, min, max) {
        return Math.min(Math.max(value, min), max);
    }

    function animateNumbers() {
        $$("[data-count]").forEach((node) => {
            const raw = Number.parseFloat(node.dataset.count || "0");
            const suffix = node.dataset.suffix || "";
            const decimals = Number.isInteger(raw) ? 0 : 2;
            const start = performance.now();
            const duration = 760;

            function tick(now) {
                const progress = clamp((now - start) / duration, 0, 1);
                const eased = 1 - Math.pow(1 - progress, 3);
                const value = raw * eased;
                node.textContent = `${value.toFixed(decimals)}${suffix}`;
                if (progress < 1) {
                    requestAnimationFrame(tick);
                } else {
                    node.textContent = `${raw.toLocaleString(undefined, {
                        maximumFractionDigits: decimals,
                    })}${suffix}`;
                }
            }

            requestAnimationFrame(tick);
        });
    }

    function initIcons() {
        if (window.lucide && typeof window.lucide.createIcons === "function") {
            window.lucide.createIcons();
        }
    }

    function initShellControls() {
        const savedTheme = localStorage.getItem("securepay-theme");
        if (savedTheme === "dark" || savedTheme === "light") {
            document.documentElement.dataset.theme = savedTheme;
        }

        const themeButton = $("[data-theme-toggle]");
        if (themeButton) {
            themeButton.addEventListener("click", () => {
                const nextTheme = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
                document.documentElement.dataset.theme = nextTheme;
                localStorage.setItem("securepay-theme", nextTheme);
            });
        }

        const sidebarButton = $("[data-sidebar-toggle]");
        if (sidebarButton) {
            sidebarButton.setAttribute("aria-pressed", String(document.body.classList.contains("sidebar-collapsed")));
            sidebarButton.addEventListener("click", () => {
                document.body.classList.toggle("sidebar-collapsed");
                sidebarButton.setAttribute("aria-pressed", String(document.body.classList.contains("sidebar-collapsed")));
            });
        }
    }

    function initCommandPalette() {
        const palette = $("[data-command-palette]");
        const input = $("[data-command-input]");
        const results = $("[data-command-results]");
        if (!palette || !input || !results) return;

        function readableLabel(link) {
            const clone = link.cloneNode(true);
            $$(".nav-icon", clone).forEach((icon) => icon.remove());
            return clone.textContent.trim();
        }

        const links = $$(".nav-link, .quick-actions a, .hero-actions a").map((link) => ({
            label: readableLabel(link),
            href: link.href,
        }));

        function render(query = "") {
            const normalized = query.trim().toLowerCase();
            const matches = links
                .filter((item, index, list) => {
                    const firstIndex = list.findIndex((candidate) => candidate.href === item.href);
                    return firstIndex === index && (!normalized || item.label.toLowerCase().includes(normalized));
                })
                .slice(0, 8);

            results.innerHTML = matches.length
                ? matches.map((item) => `<a href="${item.href}">${item.label}</a>`).join("")
                : '<span class="muted">No matching workspace action.</span>';
        }

        function openPalette() {
            palette.hidden = false;
            render();
            requestAnimationFrame(() => input.focus());
        }

        function closePalette() {
            palette.hidden = true;
            input.value = "";
        }

        $$("[data-command-open]").forEach((button) => button.addEventListener("click", openPalette));
        $$("[data-command-close]").forEach((button) => button.addEventListener("click", closePalette));
        input.addEventListener("input", () => render(input.value));
        palette.addEventListener("click", (event) => {
            if (event.target === palette) closePalette();
        });
        document.addEventListener("keydown", (event) => {
            if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
                event.preventDefault();
                openPalette();
            }
            if (event.key === "Escape" && !palette.hidden) closePalette();
        });
    }

    function initPredictionForm() {
        const form = $("[data-prediction-form]");
        if (!form) return;

        const inputs = $$("input[type='number']", form);
        const progress = $("[data-feature-progress]");
        const amountPreview = $("[data-amount-preview]");
        const timePreview = $("[data-time-preview]");
        const signalPreview = $("[data-signal-preview]");

        function updatePreview() {
            const filled = inputs.filter((input) => input.value !== "").length;
            const percent = Math.round((filled / inputs.length) * 100);
            if (progress) {
                progress.style.setProperty("--progress", `${percent}%`);
                progress.dataset.label = `${percent}% complete`;
            }

            const amount = Number.parseFloat($("input[name='Amount']", form)?.value || "0");
            const time = Number.parseFloat($("input[name='Time']", form)?.value || "0");
            const nonZero = inputs.filter((input) => Math.abs(Number.parseFloat(input.value || "0")) > 0).length;

            if (amountPreview) amountPreview.textContent = `$${amount.toLocaleString(undefined, { maximumFractionDigits: 2 })}`;
            if (timePreview) timePreview.textContent = `${Math.round(time).toLocaleString()} sec`;
            if (signalPreview) signalPreview.textContent = `${nonZero}/${inputs.length}`;
        }

        $$("[data-sample-fill]").forEach((button) => {
            button.addEventListener("click", () => {
                const values = JSON.parse(button.dataset.sampleValues || "{}");
                Object.entries(values).forEach(([key, value]) => {
                    const input = $(`input[name='${key}']`, form);
                    if (input) input.value = value;
                });
                updatePreview();
                form.scrollIntoView({ behavior: "smooth", block: "start" });
            });
        });

        inputs.forEach((input) => input.addEventListener("input", updatePreview));
        updatePreview();
    }

    function initDropzones() {
        $$("[data-dropzone]").forEach((zone) => {
            const input = $("input[type='file']", zone);
            const label = $("[data-file-label]", zone);
            if (!input || !label) return;

            function updateLabel() {
                label.textContent = input.files.length ? input.files[0].name : "Drop CSV here or browse";
            }

            ["dragenter", "dragover"].forEach((eventName) => {
                zone.addEventListener(eventName, (event) => {
                    event.preventDefault();
                    zone.classList.add("is-dragging");
                });
            });

            ["dragleave", "drop"].forEach((eventName) => {
                zone.addEventListener(eventName, (event) => {
                    event.preventDefault();
                    zone.classList.remove("is-dragging");
                });
            });

            zone.addEventListener("drop", (event) => {
                if (event.dataTransfer.files.length) {
                    input.files = event.dataTransfer.files;
                    updateLabel();
                }
            });

            input.addEventListener("change", updateLabel);
            updateLabel();
        });
    }

    function initTables() {
        $$("[data-table-panel]").forEach((panel) => {
            const table = $(".data-table", panel);
            const search = $("[data-table-search]", panel);
            if (!table) return;

            if (search) {
                search.addEventListener("input", () => {
                    const query = search.value.trim().toLowerCase();
                    $$("tbody tr", table).forEach((row) => {
                        row.hidden = query && !row.textContent.toLowerCase().includes(query);
                    });
                });
            }

            $$("th", table).forEach((header, index) => {
                header.tabIndex = 0;
                header.dataset.sortable = "true";
                header.addEventListener("click", () => sortTable(table, index, header));
                header.addEventListener("keydown", (event) => {
                    if (event.key === "Enter" || event.key === " ") {
                        event.preventDefault();
                        sortTable(table, index, header);
                    }
                });
            });
        });
    }

    function sortTable(table, columnIndex, header) {
        const tbody = $("tbody", table);
        if (!tbody) return;

        const current = header.dataset.sortDirection === "asc" ? "desc" : "asc";
        $$("th", table).forEach((item) => {
            item.dataset.sortDirection = "";
        });
        header.dataset.sortDirection = current;

        const rows = $$("tr", tbody);
        rows.sort((a, b) => {
            const aValue = (a.children[columnIndex]?.textContent || "").trim();
            const bValue = (b.children[columnIndex]?.textContent || "").trim();
            const aNumber = Number.parseFloat(aValue.replace(/[$,%]/g, ""));
            const bNumber = Number.parseFloat(bValue.replace(/[$,%]/g, ""));
            const bothNumeric = Number.isFinite(aNumber) && Number.isFinite(bNumber);

            if (bothNumeric) {
                return current === "asc" ? aNumber - bNumber : bNumber - aNumber;
            }

            return current === "asc"
                ? aValue.localeCompare(bValue)
                : bValue.localeCompare(aValue);
        });
        rows.forEach((row) => tbody.appendChild(row));
    }

    function initRiskSimulator() {
        const simulator = $("[data-risk-simulator]");
        if (!simulator) return;

        const amount = $("[data-sim-amount]", simulator);
        const velocity = $("[data-sim-velocity]", simulator);
        const trust = $("[data-sim-trust]", simulator);
        const score = $("[data-sim-score]", simulator);
        const band = $("[data-simulator-band]", simulator);
        const action = $("[data-sim-action]", simulator);
        const detail = $("[data-sim-detail]", simulator);
        const ring = $("[data-sim-ring]", simulator);
        const amountLabel = $("[data-sim-amount-label]", simulator);
        const velocityLabel = $("[data-sim-velocity-label]", simulator);
        const trustLabel = $("[data-sim-trust-label]", simulator);

        if (!amount || !velocity || !trust || !score || !band || !action || !detail || !ring) return;

        function update() {
            const amountValue = Number.parseFloat(amount.value);
            const velocityValue = Number.parseFloat(velocity.value);
            const trustValue = Number.parseFloat(trust.value);
            const amountRisk = clamp((amountValue / 5000) * 42, 0, 42);
            const velocityRisk = clamp(velocityValue * 0.38, 0, 38);
            const trustRisk = clamp((100 - trustValue) * 0.34, 0, 34);
            const risk = clamp(Math.round(amountRisk + velocityRisk + trustRisk), 0, 100);

            let level = "LOW";
            let nextAction = "Approve under normal controls";
            let nextDetail = "Low-risk profile with normal review requirements.";
            if (risk >= 85) {
                level = "CRITICAL";
                nextAction = "Hold transaction and escalate immediately";
                nextDetail = "Critical profile. Route to senior fraud review before settlement.";
            } else if (risk >= 60) {
                level = "HIGH";
                nextAction = "Require step-up verification";
                nextDetail = "High-risk profile. Verify customer and inspect recent activity.";
            } else if (risk >= 30) {
                level = "MEDIUM";
                nextAction = "Monitor and review context";
                nextDetail = "Medium-risk profile. Compare against customer behavior before approval.";
            }

            score.textContent = `${risk}%`;
            band.textContent = level;
            band.dataset.level = level.toLowerCase();
            action.textContent = nextAction;
            detail.textContent = nextDetail;
            ring.style.setProperty("--risk", `${risk}%`);
            if (amountLabel) amountLabel.textContent = `$${amountValue.toLocaleString()}`;
            if (velocityLabel) velocityLabel.textContent = `${velocityValue}`;
            if (trustLabel) trustLabel.textContent = `${trustValue}`;
        }

        [amount, velocity, trust].forEach((input) => input.addEventListener("input", update));
        update();
    }

    function initCharts() {
        if (!window.Plotly) return;
        $$(".plotly-graph-div").forEach((chart) => {
            window.Plotly.Plots.resize(chart);
        });
        window.addEventListener("resize", () => {
            $$(".plotly-graph-div").forEach((chart) => window.Plotly.Plots.resize(chart));
        });
    }

    function initFormLoadingStates() {
        $$("form").forEach((form) => {
            const method = (form.getAttribute("method") || "get").toLowerCase();
            if (method !== "post") return;

            form.addEventListener("submit", () => {
                form.classList.add("is-submitting");
                const submitter = $("button[type='submit']", form);
                if (submitter) {
                    submitter.setAttribute("aria-busy", "true");
                }
            });
        });
    }

    function initRiskMeters() {
        $$("[data-risk-meter]").forEach((meter) => {
            const value = clamp(Number.parseFloat(meter.dataset.riskMeter || "0"), 0, 100);
            meter.style.setProperty("--risk", `${value}%`);
        });
    }

    document.addEventListener("DOMContentLoaded", () => {
        initIcons();
        initShellControls();
        animateNumbers();
        initCommandPalette();
        initPredictionForm();
        initDropzones();
        initTables();
        initRiskMeters();
        initRiskSimulator();
        initCharts();
        initFormLoadingStates();
    });
})();
