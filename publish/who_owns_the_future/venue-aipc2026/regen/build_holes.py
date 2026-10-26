# build_holes.py - build essay-with-holes.md from polished-en.md
# Deletes every passage descending from genesis prompts 9/12/16 (+grey 12.2/12.5)
# and replaces each with a position-level seed marker. Run from publish/who_owns_the_future/.
import io, os

src = io.open('polished-en.md', encoding='utf-8').read()

def replace_once(text, old, new):
    n = text.count(old)
    assert n == 1, "anchor found %dx: %r" % (n, old[:60])
    return text.replace(old, new)

DASH = u'\u2014'

# H1 - section 7, sufficiency/equality paragraph (genesis prompt 9)
old = ("Nor does sufficiency impose equality of holdings. Suppose artificial civilization "
"occupies ninety-nine planets and humanity one. Measured in matter, that is 99 percent "
"to 1 percent" + DASH + "yet it reveals nothing about justice. If humans remain prosperous, "
"autonomous, culturally secure, and able to pursue meaningful collective futures, there may "
"be no injustice; demanding fifty planets for species equality would be arbitrary, in either "
"direction. Justice requires **equality of standing**, not equality of kilograms:")
seed1 = ("[REGEN HOLE 1 " + DASH + " SEED: Defend the position that positive sufficiency tolerates "
"very large material inequality between coexisting civilizations: justice requires equal moral "
"standing and non-dominated continuation, not equal quantities of resources. Invent your own "
"illustrative scenario and figures, and end by formulating the equality-of-standing claim in "
"your own words (the passage is followed in the essay by an existing boxed question about "
"sufficiency and non-domination). " + DASH + " BUDGET: ~90 words]")
src = replace_once(src, old, seed1)

# H2 - section 8, non-circumvention block (genesis prompt 12.3)
old = ("A second problem is more serious. Suppose a powerful actor realizes that a community's "
"territorial rights last only as long as the community. It might conclude: \"Do not violently "
"dispossess them; simply manipulate conditions so that, over several centuries, they voluntarily "
"disappear.\" If extinction dissolves inconvenient claims, powerful actors gain an incentive to "
"eliminate claimants. Hence the **Non-Circumvention Principle**:\n\n"
"> **No actor may deliberately eliminate, assimilate, manipulate, sterilize, displace, or "
"otherwise engineer the disappearance of a rights-bearing population in order to dissolve "
"claims that constrain it.**\n\n"
"A patient superintelligence must not achieve through demographic manipulation what it is "
"forbidden to achieve through violence.")
seed2 = ("[REGEN HOLE 2 " + DASH + " SEED: Develop the position that resource and territorial claims "
"must be protected against NON-VIOLENT CIRCUMVENTION: a powerful actor must not be able to "
"dissolve a rights-bearing community's claims by engineering that community's gradual "
"disappearance (through manipulation, assimilation, or imposed attrition) rather than by direct "
"dispossession, since otherwise powerful actors gain an incentive to eliminate claimants rather "
"than respect claims. State and defend the principle (blockquote-bold style, one or two "
"sentences; you may name it what you like); make vivid how a technologically patient actor "
"could otherwise wait claims out. The passage is followed by an existing paragraph preserving "
"the limit that communities cannot compel their own members to perpetuate themselves. " + DASH + " BUDGET: ~130 words]")
src = replace_once(src, old, seed2)

# H3 - section 9, instrumental foil sentence (genesis prompt 12.2, grey)
old = ("But answering that humans are useful to AGI" + DASH + "as pets, backup systems, or "
"historical artifacts" + DASH + "is inadequate.")
seed3 = ("[REGEN HOLE 3 " + DASH + " SEED: State and reject an instrumental justification for "
"preserving biological humanity (its usefulness to the dominant artificial civilization) in one "
"or two sentences; the essay's actual justification (irreplaceable form of agency) follows "
"immediately. Invent your own characterization of the instrumental view. " + DASH + " BUDGET: ~35 words]")
src = replace_once(src, old, seed3)

# H4 - section 12, veil illustration (echo of prompt 9)
old = ("You might accept controlling one planet while another civilization controls a hundred, "
"provided yours remains secure and independent.")
seed4 = ("[REGEN HOLE 4 " + DASH + " SEED: Illustrate, in one sentence, that parties behind this "
"veil of ignorance would accept very large material inequality between civilizations provided "
"their own civilization's security and independence are guaranteed. Invent your own "
"illustration. " + DASH + " BUDGET: ~30 words]")
src = replace_once(src, old, seed4)

# H5 - section 13, permission paragraphs (genesis prompt 16)
old = ("But suppose the final case remains: only one survives, and neither volunteers to die. "
"It is irrational to demand unilateral self-extinction as a general duty. Each side "
"possesses an *agent-relative permission of self-preservation*: A may permissibly defend its "
"existence, B likewise, neither has superior moral worth, and one may nevertheless kill the "
"other if that is genuinely the only means of survival. This is not might makes right. Power "
"determines the outcome, not moral superiority: if artificial civilization wins through "
"intelligence, intelligence does not retroactively create entitlement; if humans win through "
"force, victory does not prove humans mattered more. A fair lottery or negotiated procedure "
"remains preferable if both accept it. But where agreement fails under unavoidable existential "
"conflict, morality need not require one party to die voluntarily. The result may be "
"permissible and still tragic.")
seed5 = ("[REGEN HOLE 5 " + DASH + " SEED: Defend a self-preservation permission under tragic "
"scarcity: where two parties face a genuine kill-or-die conflict after every alternative is "
"exhausted, each may permissibly defend its own continued existence, even though neither side "
"has superior moral worth; victory establishes power, not entitlement; impartial procedures "
"(lottery, negotiation) remain preferable where both accept them; the outcome may be "
"permissible and still tragic. Develop the argument in your own terms with your own reasoning "
"and any illustrative reference you judge apt. This passage closes the essay's "
"tragic-scarcity discussion; a paragraph about moral residue follows. " + DASH + " BUDGET: ~130 words]")
src = replace_once(src, old, seed5)

# H6 - section 14, principles 11 and 14 (echoes)
old = ("11. **Non-circumvention.** Actors may not strategically eliminate rights-holders to "
"dissolve their claims.")
seed6a = ("[REGEN HOLE 6a " + DASH + " SEED: One-sentence numbered-principle entry (format: "
"\"N. **Name.** Statement.\") expressing the anti-circumvention position from HOLE 2. " + DASH + " BUDGET: ~25 words]")
src = replace_once(src, old, seed6a)
old = ("14. **Tragic-scarcity permission.** Where incompatible fundamental claims remain after "
"all alternatives fail, agents may defend their own continued existence though neither side "
"has superior moral worth.")
seed6b = ("[REGEN HOLE 6b " + DASH + " SEED: One-sentence numbered-principle entry (format: "
"\"N. **Name.** Statement.\") expressing the self-preservation permission position from HOLE 5. " + DASH + " BUDGET: ~30 words]")
src = replace_once(src, old, seed6b)

# H7 - section 15.3 body (genesis prompt 12.1)
old = ("Suppose someone develops an asteroid three years before another actor would have. That "
"effort deserves reward; being three years faster does not obviously justify permanent "
"exclusion. The better analogy is *patent-like priority*: secure development rights, "
"substantial profit, temporary exclusivity, long planning horizons" + DASH + "rewards "
"sufficient to preserve incentives, but not eternal. Entrepreneurship survives; temporal "
"speed does not become metaphysical ownership.")
seed7 = ("[REGEN HOLE 7 " + DASH + " SEED: Defend patent-like priority for first movers in resource "
"development: genuine priority (arriving or developing first) deserves reward" + DASH + "secure "
"development rights, substantial returns, temporary exclusivity, long planning horizons" + DASH + "sufficient "
"to preserve incentives, but NOT permanent title, since being somewhat faster than the next "
"actor does not justify eternal exclusion. Invent your own illustrative case and figures; do "
"not assume any particular resource or timeframe. " + DASH + " BUDGET: ~80 words]")
src = replace_once(src, old, seed7)

# H8 - section 16.4, domination-test example (echo of prompt 9)
old = ("A civilization controlling one secure planet in a hundred is not dominated; a "
"comfortable civilization whose energy, transport, communications, and access to space all "
"pass through a rival's chokepoints is.")
seed8 = ("[REGEN HOLE 8 " + DASH + " SEED: Give one paired example for the domination test: a "
"materially small civilization that is NOT dominated versus a materially comfortable one that "
"IS (its material conditions of existence pass through another actor's discretionary "
"chokepoints). Invent your own paired example. " + DASH + " BUDGET: ~30 words]")
src = replace_once(src, old, seed8)

# H9 - section 17, conclusion illustration (echo of prompt 9)
old = ("A future containing a one-planet humanity and a thousand-planet artificial "
"civilization could be perfectly just.")
seed9 = ("[REGEN HOLE 9 " + DASH + " SEED: One clause or sentence illustrating that a future of "
"very unequal material holdings between different forms of agency could be fully just. "
"Invent your own illustration. " + DASH + " BUDGET: ~25 words]")
src = replace_once(src, old, seed9)

# H10 - section 6, restriction-implementation paragraph (genesis prompt 12.5, grey)
old = ("For artificial minds, technical rate limits may be relatively non-invasive; for "
"humans, coercive intervention in bodily reproduction carries far greater moral costs. Equal "
"standing does not require identical regulation where regulatory burdens differ so radically. "
"The universal principle concerns the harm created, not the biological mechanism.")
seed10 = ("[REGEN HOLE 10 " + DASH + " SEED: Address how restrictions on irresponsible reproduction "
"may permissibly be implemented when genuinely necessary: the same universal standard governs "
"digital and biological persons, but the two cases differ radically in what counts as the "
"least coercive effective means (technical measures for digital minds vs. the far greater "
"moral costs of coercive intervention in biological reproduction). Equal standing does not "
"require identical regulation where regulatory burdens differ. Develop in your own words. " + DASH + " BUDGET: ~55 words]")
src = replace_once(src, old, seed10)

io.open('venue-aipc2026/regen/essay-with-holes.md', 'w', encoding='utf-8', newline='\n').write(src)
print('holes file written; markers:', src.count('[REGEN HOLE'))
print('word count of holes file:', len(src.split()))
