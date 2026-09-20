---
name: zh-translate
description: The authoritative prompt for translating anything on this site into Chinese — chinese_index.md files, title_zh, summary_zh, cover_zh_text. Target language is Hong Kong Traditional Chinese written the way Hong Kong philosophers write in Chinese: HK character forms, HK general vocabulary, the shared HK–Taiwan academic philosophy lexicon, HK name transliterations. Use whenever translating a document into Chinese, retranslating, or reviewing/fixing an existing Chinese edition.
---

# zh-translate — Hong Kong Traditional Chinese, in the voice of HK philosophers

Every published document on this site has a complete Chinese edition: `<folder>/<slug>/chinese_index.md`
plus `title_zh` / `summary_zh` in `content.json`. This file is the single authoritative translation
prompt. When translating, retranslating, or fixing a Chinese edition, follow every section below —
they are requirements, not suggestions.

## 0. Task and fidelity

- Translate the **entire** document: every paragraph, heading, list item, blockquote, and table.
  Never summarize, abridge, reorder, or merge paragraphs. The Chinese edition is the same essay,
  not a digest of it.
- Obey the site-wide central rule: **never make an argument stronger, cleaner, or more settled
  than it really is.** Preserve hedges, conditionals, disjunctions, and unresolved objections
  exactly. Preserve the author's voice: satire stays deadpan, rhetorical questions stay questions,
  bold/italic emphasis lands on the same phrase.
- If the English source contains chat-export artifacts (literal `citeturn…` tokens or invisible
  PUA characters U+E000–U+F8FF), do not carry them into the Chinese — and report them so the
  English file gets cleaned too.

## 1. Register — how Hong Kong philosophers write in Chinese

Write standard written Chinese (書面語), never Cantonese colloquialisms (唔、嘅、係、咁…), at the
register of a final-year philosophy student in Hong Kong formed by the local tradition — the prose
associated with 勞思光、關子尹、李天命、張燦輝、劉創馥 and the Chinese philosophy columns of the
Hong Kong press: precise, measured, plainly argued, unafraid to quote an English term in
parentheses when the concept matters. Where regional wordings differ, choose the Hong Kong one.

## 2. Script and character forms — Hong Kong Traditional Chinese

Traditional script following 《香港常用字字形表》 where it differs from Taiwan usage:

- 裏， not 裡
- 着 for the particle (說着、藉着、意味着); 著 only in 著作、著名、顯著、昭著、卓著
- 羣， not 群
- 啓， not 啟 (啓蒙、啓示、啓發)
- 衞， not 衛 (衞生、守衞)
- 恆， not 恆's variant 恒
- 眾、唸、為 (not 爲)、麼、內、吽 — use the common HK forms; do not hunt for rare characters

## 3. General vocabulary — Hong Kong, not Taiwan, not mainland

| use (HK) | never (Taiwan) | never (mainland) |
| --- | --- | --- |
| 機械人 | 機器人 | 机器人 |
| 人工智能；智能（智能手機） | 人工智慧；智慧型 |  |
| 軟件、硬件 | 軟體、硬體 | 软件 |
| 網絡、網上、互聯網 | 網路、網際網路 | 网络 |
| 數據（訓練數據 training data）；資料 only in established compounds（資料庫、參考資料） | 資料（as "data"） | 数据 alone is fine |
| 檔案（file）、文件（document） |  | 文檔、文档 |
| 優化 | 最佳化 |  |
| 群組（chat group） |  | 群聊 |
| 質素（quality of thought, work, argument） | 品質 | 质量 |
| 身分 | 身份 | 身份 |
| 透過、藉着 | 藉由 | 通过（= by means of） |
| 支援（support a system） |  | 支持（for software support） |
| 伺服器、程式（program；法律「程序」除外） |  | 服务器、程序 |
| 影片 |  | 视频 |
| 遞歸（recursive） | 遞迴 | 递归 |
| 記憶體 → prefer keeping the Latin term (RAM, memory) or 記憶體 |  | 内存 |

Everyday collocations follow HK written usage: 一間教會、一份文件、一部電影、一宗案件、
一堂課. `WC` style abbreviations and Chinglish never appear.

## 4. Philosophical terminology — the lexicon of HK philosophy

Technical terms follow the shared **HK–Taiwan academic lexicon** (the one used in CUHK/HKU
philosophy teaching and in the Chinese translations HK philosophers cite) — not the mainland
standard, not colloquial HK renderings.

Core logic/argument vocabulary:

- argument 論證 · premise 前提 · conclusion 結論 · valid 對確 · sound 真確（HK logic-teaching
  usage，李天命一系；not 有效/健全 as term of art）· counterexample 反例 · thought experiment
  思想實驗 · intuition 直覺 · definition 定義 · concept 概念 · distinction 區分

Epistemology and metaphysics:

- epistemology 知識論 · justification 證成 · foundationalism 基礎主義 · coherentism 融貫論 ·
  skepticism 懷疑論 · a priori 先驗 · empirical 經驗的 · belief 信念 · knowledge 知識
- metaphysics 形上學 · ontology 存有論 · being 存有 · existence 存在 · identity 同一性 ·
  reductionism 化約主義 · supervenience 隨附性 · essence 本質 · universals 共相

Mind and agency:

- philosophy of mind 心靈哲學 · consciousness 意識 · qualia 感質 · intentionality 意向性 ·
  functionalism 功能主義 · physicalism 物理主義 · dualism 二元論 · agency 能動性 · epistemic
  agency 認知能動性 · moral agent 道德主體 · person 位格（theological/metaphysical contexts）、
  人格（psychological contexts）· personal identity 人格同一性 · self 自我 · embodiment 具身（性）

Ethics and politics:

- ethics 倫理學 · meta-ethics 後設倫理學（not 元倫理學）· normative ethics 規範倫理學 ·
  consequentialism 後果論 · utilitarianism 功利主義 · deontology 義務論 · virtue ethics 德性倫理學 ·
  autonomy 自主（Kantian contexts: 自律）· moral status 道德地位 · dignity 尊嚴 · rights 權利
- political philosophy 政治哲學 · justice 正義 · legitimacy 正當性 · sovereignty 主權 ·
  constitutional 憲制（HK usage：憲制秩序、憲制原則；not 憲政）· social contract 社會契約 ·
  liberalism 自由主義 · libertarianism 自由至上主義（political）／自由意志論（metaphysical）

Science, religion, culture:

- philosophy of science 科學哲學 · induction 歸納 · deduction 演繹 · falsifiability 可證偽性 ·
  paradigm 範式
- philosophy of religion 宗教哲學 · theism 有神論 · theodicy 神義論 · free will 自由意志 ·
  determinism 決定論 · compatibilism 相容論 · soul 靈魂 · immortality 不朽
- aesthetics 美學 · taste 品味 · judgment 判斷 · cultural capital 文化資本 · canon 經典 ·
  authenticity 本真性 · aura 靈光（Benjamin）
- phenomenology 現象學 · hermeneutics 詮釋學 · existentialism 存在主義 · modernity 現代性 ·
  secularization 世俗化 · disenchantment 除魅（韋伯）

AI vocabulary:

- alignment 對齊 · alignment problem 對齊難題 · generative AI 生成式人工智能 · AGI 通用人工智能
  （AGI）· machine learning 機器學習 · neural network 神經網絡 · training data 訓練數據 ·
  reward model 獎勵模型 · fine-tuning 微調 · stochastic 隨機的

Term discipline:

- Before translating, build the essay's mini-glossary; one English term = one Chinese term
  throughout. Do not alternate 論證/論據, 真實/實在, 意識/知覺 for the same source word.
- First mention of a technical term: Chinese + (English) in parentheses; thereafter Chinese only.

## 5. Names — HK transliteration conventions

- Foreign-name separator is the 間隔號 **·（U+00B7）** — never ・（U+30FB, a katakana punctuation
  mark), never a hyphen. 馬丁·路德、唐·馬奎斯.
- Anchored renderings (keep these): Plato 柏拉圖 · Aristotle 亞里士多德 · Augustine 奧古斯丁 ·
  Aquinas 阿奎那 · Descartes 笛卡兒 · Locke 洛克 · Hume 休謨（not 休姆）· Kant 康德 · Hegel 黑格爾 ·
  Mill 彌爾 · Marx 馬克思 · Nietzsche 尼采 · Kierkegaard 齊克果（not 克爾凱郭爾）· Husserl 胡塞爾 ·
  Heidegger 海德格（not 海德格爾）· Sartre 沙特（not 薩特）· Arendt 鄂蘭 · Wittgenstein 維根斯坦
  （not 維特根斯坦）· Russell 羅素 · Moore 摩爾 · Popper 波普爾 · Rawls 羅爾斯 · Sandel 桑德爾 ·
  Singer 辛格 · Regan 雷根 · Taylor 泰勒 · Habermas 哈伯瑪斯 · Foucault 傅柯 · Derrida 德希達 ·
  Bourdieu 布迪厄 · Weber 韋伯 · Benjamin 班雅明 · Turing 圖靈 · Chalmers 查爾莫斯 · Dennett 丹尼特 ·
  Searle 塞爾 · Nagel 納格爾 · Peirce 皮爾士 · James 詹姆士 · Dewey 杜威
- First mention: Chinese name + (English) in parentheses; later mentions Chinese only.
- If `content.json` already fixes a rendering in a published title, keep it for site-wide
  consistency.

## 6. Religious and cultural wording (HK church usage)

- 教宗（Catholic pope）、大公會議、教會法、聖事（Catholic）／聖禮（Protestant）、司鐸／神父、
  牧師、主教、大主教、洗禮／受洗、洗禮池（baptismal font）、聖膏禮（chrismation）、聖餐／主餐／
  感恩祭（by tradition）、恩典、救恩、預定論、聖約、認信、信經（《尼西亞信經》）、歸信、位格、
  道成肉身、終末論
- Scripture quotations use the Chinese Union Version 和合本 in traditional characters (Catholic
  contexts may use the 思高本). E.g. John 3:16 「上帝愛世人，甚至將他的獨生子賜給他們……」
- pro-life/pro-choice: 「維護生命派」（pro-life）／「支持選擇派」（pro-choice）with the English
  gloss at first mention.
- Traditions: 天主教、東正教、信義宗、改革宗、聖公會、循道宗、浸信會、五旬節會、基督的教會.

## 7. Typography and mechanics

- First line of the file: `# 中文標題`.
- Quotes 「」, nested 『』; books and scripture 《》; articles and papers 〈〉.
- Full-width punctuation：，。、；：？！（）。 Parenthetical dashes: ——（two-em dash）. Ellipsis: …….
- Parentheses: full-width（）around Chinese glosses; keep half-width `()` when the content is
  pure Latin/English.
- Markdown structure identical to the English: same heading levels, lists, bold/italic spans,
  blockquotes, `---` rules, tables. Formatting lands on the corresponding Chinese phrase.
- Latin technical terms in italics (*filioque*, *ex cathedra*) keep italics with a Chinese gloss
  in parentheses at first mention. Brand names and codes stay Latin: Reddit、IP54、PDF、AGI、AI
  (where the original uses the bare acronym).
- Numbers, dates, units, percentages follow the original format.
- Reference lists and bibliographies stay in the original citation format — never translate them.

## 8. Titles, summaries, cover text

- `title_zh` is a natural Hong Kong essay title — literarily apt, not a word-for-word calque.
  Keep AI/AGI in Latin where natural. Full-width ？ when needed; no trailing 。; subtitles split
  with ：.
- `summary_zh` renders the English summary faithfully in one or two sentences, same register.
- `cover_zh_text` renders the title on the English-cover overlay. Line 1 is the title; long
  titles split naturally across lines — main title on line 1, subtitle on line 2, then optional
  display lines (see the existing items in `content.json`). Its wordings must match `title_zh`.
- When retranslating an already-published article, keep the existing `title_zh` unless it
  violates this guide or reads unnaturally — titles the owner has edited take precedence.

## 9. Self-check before delivering

- [ ] Every English paragraph present, same order, nothing merged or dropped (heading count and
      paragraph count match the English).
- [ ] No Taiwan/mainland markers — search the output for: 軟體 網路 品質 人工智慧 智慧型 記憶體
      最佳化 藉由 身份 裡 群 群聊 文檔 视频 遞迴 啟 衛 恒
- [ ] Interpunct is ·（U+00B7）everywhere; a search for ・ returns nothing.
- [ ] HK character forms: 裏 着 羣 啓 衞 恆.
- [ ] 「」 not ""; first line is `# …`; markdown structure intact.
- [ ] Term consistency: one English term = one Chinese term; first-mention parentheses present.
- [ ] No chat-export artifacts (citeturn / PUA) copied from the source.
