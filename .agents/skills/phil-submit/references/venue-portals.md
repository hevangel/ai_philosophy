# Venue portal playbooks

Concrete flow notes per portal type. Always verify against the live site — portals redesign.
Where a step needs the user (login, 2FA, captcha, payment), pause and ask.

## PhilArchive (https://philarchive.org)
1. Log in with the owner's PhilPapers account (user handles login).
2. "Add an item" / direct upload: choose *Submitted to PhilArchive* (preprint) or *Published*.
3. Fill: title, abstract, keywords, subject areas (use PhilPapers categories), authors.
4. Upload PDF only. OCR requirement: the PDF must have extractable text (our pandoc→Word→PDF
   output does). Submit. No moderation gate; item appears in the archive, indexed by PhilPapers.

## PhilSci-Archive (https://philsci-archive.pitt.edu, EPrints)
1. Register/login (account email should be an academic address if the user has one).
2. Deposits: Start a new deposit → choose type (article/monograph) → metadata (title, abstract,
   keywords, subjects) → upload PDF → confirm. English only; philosophy of science scope only.
3. Eligibility gate: faculty/postdoc/grad/prior depositor/endorsed. If the owner's account
   doesn't qualify, the deposit may sit in moderation — an endorsement from a prior depositor
   is required (email template on the policy page). Moderation ~5 business days before public.

## arXiv (https://arxiv.org/submit)
1. User login (+ endorsement for first submit in a category — user action).
2. Workflow: subject class → license → files. Philosophy of science → `physics.hist-ph`
   (moderated); AI-adjacent → `cs.AI`. Upload `main.tex` (+ figures) — TeX is required if the
   paper was made with TeX; compile check runs on their AutoTeX. PDF-only submissions are
   discouraged/rejected for TeX-origin papers.
3. Metadata: authors (human only), abstract, categories (primary + secondary), journal ref.
4. Declaration: AI use must be disclosed in the manuscript itself (add an "AI assistance"
   statement in the acknowledgments before export). Verify EVERY reference before submit —
   arXiv bans submitters for one year over hallucinated references.

## SocArXiv (https://socopen.org, Janeway)
1. OSF login → New Submission. AI policy questionnaire is enforced: disclose AI use per
   https://socopen.org/ai-policy/ — only allowed categories (copy-editing, pre-writing help,
   translation, analysis) with human supervision; no verbatim LLM text. Failure to disclose =
   rejection.
2. Metadata + PDF upload → editor moderation. Rejections are appealable via their form.

## Zenodo (https://zenodo.org)
1. Login (GitHub/ORCID) → New upload → metadata (DOI minted; pick "Lesson/Paper" type,
   add license CC-BY-4.0 unless the user says otherwise) → upload PDF. Publish button is the
   irreversible step (files are immutable; new version = new DOI).

## ChinaXiv (https://chinaxiv.org)
1. Real-name registration (user handles). Submit → fill 中文标题/摘要/关键词 + English abstract
   → upload PDF. Attach the 《生成式人工智能工具使用情况说明》 as a supplementary file if AI was
   used (national labeling rules apply even without a platform policy).

## SSRN (https://hq.ssrn.com)
1. Login → Submit an article → pick a research paper series (Philosophy of Law / PSN) →
   title/abstract/keywords/JEL (skip) → upload PDF. Elsevier AI norms: disclose in the paper.
   "Submit" posts to the working-paper series after a light check.

## Editorial Manager (Springer, Elsevier, Chicago, many others)
e.g. Synthese, Philosophical Studies, Erkenntnis, Minds and Machines, Philosophy & Technology,
Ethics, Philosophy of Science.
1. https://www.editorialmanager.com/<journal-code>/ → Author login (user).
2. "Submit New Manuscript" → article type (Original Research / Article) → attach files in the
   right roles: Manuscript (blinded DOCX), Title Page (with author details, as a separate
   file), Cover Letter, Declaration of Interest, AI-use statement (some EM journals have a
   dedicated question instead — answer honestly per ai-disclosure.md).
3. Suggest reviewers only if the user provides names — never invent reviewer names.
4. Build PDF → Approve → Submit. The Approve-and-Submit is the final gate for user confirmation.

## ScholarOne (Wiley, T&F, Cambridge, OUP)
e.g. Philosophical Quarterly, Inquiry, Mind, Philosophy & Public Affairs, JAPA.
1. https://mc.manuscriptcentral.com/<journal-code> → Author Center.
2. Steps: type/title/abstract → keywords → authors/details → cover letter → file upload
   (Main Document = blinded; separate Title Page if double-blind) → Review & Submit.
3. Some journals ask "Was AI used in preparing this manuscript?" — answer per disclosure file.

## OJS / journal-native (EUJAP, Open Philosophy via Editorial Manager, MDPI SuSy)
- EUJAP: journal OJS site → register → make a submission → upload DOCX.
- MDPI (https://susy.mdpi.com): Assistant Editor flow; check APC/fees with user before final
  submit (MDPI charges article processing charges — that's a payment step, always user-gated).

## CNKI 期刊门户 cbpt.cnki.net (《自然辩证法研究》《自然辩证法通讯》 etc.)
1. Journal portal → 作者投稿系统 (作者中心) → 注册 (user does registration with real name).
2. 填写稿件信息: 题目/摘要/关键词/基金项目/作者信息 → 上传 Word 稿件 (+ 附件：《生成式人工智能
   工具使用情况说明》 if applicable, 原创承诺书 if the journal requires) → 提交.
3. Many CN portals require a 版权协议/原创声明 checkbox — read it; it typically asserts no
   undisclosed AIGC. Only tick after confirming the disclosure file matches reality.

## ajcass.com (《哲学动态》《世界哲学》)
Chinese Academy of Sciences journal system: register → 投稿 → metadata + Word upload.
Same 原创承诺/AIGC caveats as CNKI portals.
