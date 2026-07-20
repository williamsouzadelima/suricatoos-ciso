# Metodologia de Entrega vCISO — Suricatoos

> Onboarding e operação de um cliente vCISO em **100 dias**, com plano rastreável (Kanban),
> priorização (Eisenhower), controle de horas contratadas e governança por fases.
> Esta metodologia é **operacionalizada pela plataforma** (app `delivery`): o playbook
> descrito aqui é o mesmo que o comando `seed_engagement_plan` materializa como tarefas reais.

---

## 1. Princípios

1. **Entender antes de agir.** Os primeiros 30 dias são de diagnóstico; nenhuma mudança
   estrutural sem inventário, mapa regulatório e avaliação de riscos.
2. **Risco guia a prioridade.** A matriz de Eisenhower (urgência × importância) e o risco
   determinam a ordem de execução — não a ordem de chegada dos pedidos.
3. **Rastreabilidade total.** Cada atividade é uma tarefa no Kanban do cliente, com fase,
   horas estimadas, responsável e prazo. Nada vive em planilha paralela.
4. **Horas sob contrato.** Cada cliente tem um modelo de horas (orçamento, time-logging ou
   híbrido). A plataforma alerta quando o esforço estimado estoura o contratado.
5. **Governança recorrente.** Comitês e relatórios em cadência fixa; o vCISO reporta ao
   sponsor, não substitui a decisão do cliente.

---

## 2. Papéis e RACI

| Papel | Quem | Responsabilidade |
|---|---|---|
| **vCISO** | Suricatoos (líder do engajamento) | Accountable pelo programa de segurança; define estratégia, roadmap e prioridades; reporta ao sponsor. |
| **Analista de Segurança** | Suricatoos (time de entrega) | Executa avaliações, implementa/valida controles, produz evidências e relatórios. |
| **Sponsor** | Cliente (executivo — CEO/CFO/COO/Compliance) | Aprova escopo, roadmap e investimentos; remove bloqueios organizacionais. |
| **DPO / Contato Técnico** | Cliente | Consultado nas decisões técnicas e de privacidade; provê acesso, contexto e dados. |
| **Donos de Processo** | Cliente (áreas) | Informados e responsáveis por adotar os controles nas suas áreas. |

**Legenda RACI:** R = Responsável (faz) · A = Aprova (accountable) · C = Consultado · I = Informado.

| Macro-atividade | vCISO | Analista | Sponsor | DPO/Técnico |
|---|:--:|:--:|:--:|:--:|
| Kickoff e governança | A/R | C | A | C |
| Inventário de ativos e dados | A | R | I | C |
| Mapeamento regulatório | A/R | C | I | C |
| Gap assessment (ISO/NIST + setoriais) | A | R | I | C |
| Avaliação e tratamento de riscos | A/R | R | A | C |
| Quick wins de higiene | A | R | I | C |
| Estrutura de políticas | A/R | R | A | C |
| Plano de resposta a incidentes | A/R | R | C | C |
| Implementação de controles | A | R | I | C |
| Rituais de governança | A/R | C | A | I |
| Continuidade / DR | A | R | C | C |
| Gestão de terceiros | A | R | I | C |
| Relatórios executivos | A/R | C | I | I |

---

## 3. Modelo de horas (por contrato)

O engajamento seleciona **um** modelo de horas (`Engagement.hours_model`):

| Modelo | Quando usar | O que a plataforma controla |
|---|---|---|
| **budget** (Orçamento + capacidade) | Retainer com teto de horas de referência | Σ horas **estimadas** das tarefas vs `contracted_hours` → alerta de estouro (`over_budget`) e % de utilização. |
| **timelog** (Time-logging) | Faturamento por horas realizadas | Σ horas **lançadas** (TimeEntry) vs teto → burn-down (Fase 2). |
| **hybrid** (Híbrido) | Teto contratado + medição do realizado | Estimado **e** lançado lado a lado. |
| **none** | Escopo fechado sem controle de horas | Apenas progresso por fase. |

> **Cliente-padrão (setor financeiro):** inicia em **budget + capacidade**, retainer flexível /
> sob demanda. O teto contratado serve de referência; o alerta de estouro é um sinal de
> negociação/repriorização, não um bloqueio.

---

## 4. As três fases (30 / 60 / 100)

### Fase 1 — Dias 0–30 · Diagnóstico & Descoberta
*Objetivo: entender ambiente, ativos, riscos e obrigações regulatórias antes de agir.*
Kickoff e governança · Inventário de ativos e dados · Mapa de stakeholders · Mapeamento
regulatório aplicável · Gap assessment (ISO 27001 + NIST CSF + setoriais) · Levantamento de
top-risks · Avaliação de postura técnica (identidade/MFA, endpoints, rede, backup, logging) ·
**Marco:** Relatório de diagnóstico + apresentação ao sponsor.

### Fase 2 — Dias 31–60 · Quick Wins & Roadmap
*Objetivo: estancar riscos evidentes e desenhar o roadmap aprovado pelo comitê.*
Priorização dos gaps (risco × esforço) · Quick wins de higiene (MFA, patch crítico, backup
validado, hardening, revisão de acessos) · Plano de tratamento de riscos (roadmap 12 meses) ·
Estrutura de políticas (PSI, gestão de incidentes com reporte regulatório, acesso,
continuidade) · KPIs/métricas · Plano de resposta a incidentes · **Marco:** Roadmap aprovado
pelo comitê.

### Fase 3 — Dias 61–100 · Execução & Governança
*Objetivo: operar o programa — implementar controles prioritários e instituir governança.*
Implementar controles P1 do roadmap · Instituir rituais de governança · Publicar/aprovar
políticas · Continuidade e DR (PCN + teste) · Gestão de terceiros/fornecedores · Métricas em
operação + dashboard · Simulação de incidente (tabletop) · **Marco:** Relatório de fechamento
dos 100 dias + plano de continuidade do vCISO.

---

## 5. Módulos regulatórios (por sub-setor)

O intake seleciona o **sub-setor** e ativa os módulos regulatórios correspondentes, que
**somam tarefas** às três fases (mescladas por `phase_key`):

| Sub-setor (`ClientIntake.subsector`) | Módulos | Tarefas somadas (exemplos) |
|---|---|---|
| **Banco / instituição de crédito** | BACEN + LGPD | Política de segurança cibernética (Res. BCB 85 / CMN 4.893), plano de resposta a incidentes reportáveis, due diligence de nuvem, testes. |
| **Gestora / asset (ANBIMA)** | ANBIMA + LGPD | Política de segurança e continuidade do Código de Administração, segregação de funções, PCN. |
| **Corretora / DTVM (CVM)** | CVM + LGPD | Controles de mercado/custódia, suitability, requisitos de cibersegurança da CVM. |
| **Outro / híbrido** | Selecionável | Combinação conforme frameworks aplicáveis. |

> **Módulo LGPD** (transversal a todos): RoPA (registro de operações de tratamento),
> avaliação de bases legais e direitos do titular, governança de privacidade (DPO e ritos).

Frameworks-alvo do cliente financeiro: **ISO 27001:2022, LGPD, BACEN, NIST CSF 2.0, ANBIMA, CVM**.

---

## 6. Cadência de governança

| Rito | Frequência | Participantes | Saída |
|---|---|---|---|
| Status de execução | Semanal | vCISO + Analista + Contato técnico | Atualização do Kanban, bloqueios |
| Comitê técnico | Quinzenal | vCISO + time do cliente | Decisões técnicas, repriorização |
| Comitê executivo | Mensal | vCISO + Sponsor | Progresso por fase, horas, riscos, aprovações |
| Reporte executivo | Mensal / marco | vCISO → Sponsor | Relatório (PPTX branded) |

O ritmo **escala com o retainer**: contratos menores condensam os ritos; maiores adicionam
comitês de risco/privacidade dedicados.

---

## 7. Processo de onboarding (ponta a ponta)

```
Intake (questionário)         → ClientIntake (sub-setor + frameworks + contatos + ativos)
   │
Provisionar estrutura         → create_client_folder → Folder DOMAIN + Engagement
   │
Semear plano de 100 dias      → seed_engagement_plan (núcleo + módulos por phase_key)
   │                             ⇒ AppliedControls reais no Kanban do cliente + PlanTasks
Operar                        → Kanban + Eisenhower + rituais + (time-logging, Fase 2)
   │
Reportar                      → dashboard do engajamento + PPTX (Fase 2)
   │
Renovar                       → novo Engagement (histórico preservado)
```

**Como o plano vira execução:** o seed materializa cada item do playbook como um
`AppliedControl` no folder (domínio) do cliente — logo aparece no **Kanban existente**,
no **calendário** e em **"minhas tarefas"** —, com uma camada `PlanTask` guardando fase,
horas estimadas e os eixos de Eisenhower. Idempotente por `template_key`.

**Derivação de Eisenhower:** *Importância* = prioridade P1/P2 (ou override). *Urgência* =
prioridade P1 **ou** prazo (`eta`) dentro do horizonte (padrão 21 dias, ou override).
Quadrantes: Fazer (U×I) · Agendar (¬U×I) · Delegar (U×¬I) · Eliminar (¬U×¬I).

---

## 8. Referências de plataforma

- App backend: `backend/delivery/` (modelos `Engagement`, `ClientIntake`, `EngagementPhase`,
  `PlanTask`, `TimeEntry`).
- Playbook: `backend/delivery/playbooks/vciso_100d_core.yaml` + `mod_*.yaml`.
- Seed: `manage.py seed_engagement_plan --folder <cliente> --create-folder --hours <N>
  --day-zero <YYYY-MM-DD> --modules lgpd,bacen,...`
- API: `/api/delivery/engagements/{id}/{capacity,dashboard,seed_plan}`,
  `/api/delivery/plan-tasks/{eisenhower,reorder}`.

*Aditivo por design: o app `delivery` não modifica nenhum modelo do núcleo do CISO Assistant —
só relaciona por chave estrangeira, preservando a atualização com o upstream.*
