# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# -- Figura 1: Pipeline flow --
def fig_pipeline_flow():
    W, H = 980, 480
    frags = []

    frags.append(rect(40, 60, 430, 380, fill='#f8fafc', stroke='#cbd5e1', sw=1.5, rx=8))
    frags.append(text(255, 90, 'Continuous Integration (CI)', size=13, bold=True, color='#1e293b'))
    frags.append(text(255, 110, 'Automated verification and rapid feedback', size=11, color=MUTED))

    c1, w1, h1 = textbox(135, 175, 'Commit in Main\n(Trunk / PR)', size=12, bold=True, fill='#ffffff', stroke=LINE, sw=1.5, pad=10)
    frags.append(c1)

    c2, w2, h2 = textbox(345, 175, 'Static Analysis\nLinting, Types, SAST', size=12, bold=True, fill='#ffffff', stroke=NEG, sw=1.5, pad=10)
    frags.append(c2)

    c3, w3, h3 = textbox(135, 305, 'Unit Tests\nFast Isolation', size=12, bold=True, fill='#ffffff', stroke=NEG, sw=1.5, pad=10)
    frags.append(c3)

    c4, w4, h4 = textbox(345, 305, 'Artifact Build\nHermetic OCI, SBOM', size=12, bold=True, fill='#ffffff', stroke=FIELD, sw=1.8, pad=10)
    frags.append(c4)

    frags.append(arrow(200, 175, 260, 175, color=LINE, sw=1.5))
    frags.append(arrow(345, 215, 345, 260, color=LINE, sw=1.5))
    frags.append(arrow(135, 215, 135, 260, color=LINE, sw=1.5))
    frags.append(arrow(200, 305, 255, 305, color=FIELD, sw=1.8))

    c_art, wa, ha = textbox(530, 240, 'Artifact Registry\nSigned Image\n(Immutable CAS)', size=12, bold=True, fill='#ecfdf5', stroke=FIELD, sw=2, pad=12)
    frags.append(c_art)
    frags.append(arrow(435, 305, 465, 275, color=FIELD, sw=2))

    frags.append(rect(610, 60, 340, 380, fill='#f8fafc', stroke='#cbd5e1', sw=1.5, rx=8))
    frags.append(text(780, 90, 'Continuous Delivery / Deploy (CD)', size=13, bold=True, color='#1e293b'))
    frags.append(text(780, 110, 'Environment Verification and Release', size=11, color=MUTED))

    c5, w5, h5 = textbox(780, 175, 'Staging / Ephemeral Env\nIntegration & E2E Tests', size=12, bold=True, fill='#ffffff', stroke=NEG, sw=1.5, pad=10)
    frags.append(c5)
    frags.append(arrow(600, 220, 680, 185, color=FIELD, sw=1.8))

    c6_deliv, w6a, h6a = textbox(780, 290, 'Continuous Delivery\nManual Release Gate', size=11, bold=True, fill='#fffbeb', stroke='#d97706', sw=1.5, pad=8)
    frags.append(c6_deliv)

    c6_deploy, w6b, h6b = textbox(780, 385, 'Continuous Deployment\nAutomated Canary / SLO', size=11, bold=True, fill='#f0fdf4', stroke=FIELD, sw=1.5, pad=8)
    frags.append(c6_deploy)

    frags.append(arrow(780, 215, 780, 255, color='#d97706', sw=1.5))
    frags.append(arrow(780, 325, 780, 350, color=FIELD, sw=1.5))

    render(os.path.join(IMG, 'ci-cd-pipeline-flow.svg'), W, H, *frags,
           title='Pipeline Stages: Verification, Immutable Artifact, and Delivery')


# -- Figura 2: Batch Size & Lead Time --
def fig_batch_size_lead_time():
    W, H = 940, 440
    frags = []

    frags.append(rect(40, 60, 410, 340, fill='#fff5f5', stroke=POS, sw=1.5, rx=8))
    frags.append(text(245, 90, 'Big Batch Integration', size=13, bold=True, color=POS))
    frags.append(text(245, 110, 'Long-lived branches, monthly releases', size=11, color=MUTED))

    b1, _, _ = textbox(245, 160, 'Accumulation of hundreds of changes\n(Weeks of isolated branch work)', size=11, fill='#ffffff', stroke=POS, sw=1.2, pad=8)
    frags.append(b1)
    b2, _, _ = textbox(245, 235, 'Merge Hell & Semantic Conflicts\nIncompatible database migrations', size=11, fill='#ffffff', stroke=POS, sw=1.2, pad=8)
    frags.append(b2)
    b3, _, _ = textbox(245, 315, 'Manual midnight deploy\nHigh blast radius and downtime', size=11, fill='#ffffff', stroke=POS, sw=1.2, pad=8)
    frags.append(b3)

    frags.append(arrow(245, 190, 245, 205, color=POS, sw=1.5))
    frags.append(arrow(245, 265, 245, 285, color=POS, sw=1.5))
    frags.append(text(245, 375, 'MTTR: days or weeks', size=11, bold=True, color=POS))

    frags.append(rect(490, 60, 410, 340, fill='#f0fdf4', stroke=FIELD, sw=1.5, rx=8))
    frags.append(text(695, 90, 'Continuous Integration (Small Batch)', size=13, bold=True, color=FIELD))
    frags.append(text(695, 110, 'Trunk-based development, daily merges', size=11, color=MUTED))

    s1, _, _ = textbox(695, 160, 'Small atomic commits\n(A few lines or single behavior)', size=11, fill='#ffffff', stroke=FIELD, sw=1.2, pad=8)
    frags.append(s1)
    s2, _, _ = textbox(695, 235, 'Instant automated feedback loop\nDefect localized to single commit', size=11, fill='#ffffff', stroke=FIELD, sw=1.2, pad=8)
    frags.append(s2)
    s3, _, _ = textbox(695, 315, 'Automated low-risk release\nRapid canary and trivial rollback', size=11, fill='#ffffff', stroke=FIELD, sw=1.2, pad=8)
    frags.append(s3)

    frags.append(arrow(695, 190, 695, 205, color=FIELD, sw=1.5))
    frags.append(arrow(695, 265, 695, 285, color=FIELD, sw=1.5))
    frags.append(text(695, 375, 'MTTR: minutes', size=11, bold=True, color=FIELD))

    render(os.path.join(IMG, 'batch-size-lead-time.svg'), W, H, *frags,
           title='Impact of Batch Size on Delivery Speed and Operational Stability')


# -- Figura 3: DAG runner execution --
def fig_runner_dag():
    W, H = 940, 420
    frags = []

    in_box, _, _ = textbox(90, 210, 'Git Push\n(Branch commit)', size=12, bold=True, fill='#f1f5f9', stroke=LINE, sw=1.5, pad=10)
    frags.append(in_box)

    t_lint, _, _ = textbox(300, 100, 'Job: lint\n(Static Checks)', size=11, bold=True, fill='#ffffff', stroke=NEG, sw=1.4, pad=8)
    frags.append(t_lint)

    t_unit, _, _ = textbox(300, 190, 'Job: unit-test\n(Unit Suite)', size=11, bold=True, fill='#ffffff', stroke=NEG, sw=1.4, pad=8)
    frags.append(t_unit)

    t_sec, _, _ = textbox(300, 280, 'Job: sec-scan\n(SAST & Secrets)', size=11, bold=True, fill='#ffffff', stroke=NEG, sw=1.4, pad=8)
    frags.append(t_sec)

    t_build, _, _ = textbox(300, 360, 'Job: compile\n(Binary Build)', size=11, bold=True, fill='#ffffff', stroke=FIELD, sw=1.4, pad=8)
    frags.append(t_build)

    frags.append(arrow(150, 190, 215, 115, color=LINE, sw=1.4))
    frags.append(arrow(165, 205, 220, 195, color=LINE, sw=1.4))
    frags.append(arrow(165, 215, 220, 270, color=LINE, sw=1.4))
    frags.append(arrow(150, 230, 215, 345, color=LINE, sw=1.4))

    cache_box, _, _ = textbox(520, 80, 'Shared Build Cache\n(CAS / sccache / ccache)', size=10, fill='#fef3c7', stroke='#d97706', sw=1.2, pad=6)
    frags.append(cache_box)
    frags.append(line(385, 360, 460, 120, color='#d97706', sw=1.2, dash='3,3'))

    pkg_box, _, _ = textbox(560, 235, 'Job: docker-build\nBuild OCI Image\n+ Cosign Attest', size=12, bold=True, fill='#f0fdf4', stroke=FIELD, sw=1.8, pad=10)
    frags.append(pkg_box)

    frags.append(arrow(385, 110, 480, 205, color=FIELD, sw=1.4))
    frags.append(arrow(385, 190, 465, 225, color=FIELD, sw=1.4))
    frags.append(arrow(385, 280, 465, 245, color=FIELD, sw=1.4))
    frags.append(arrow(385, 355, 480, 265, color=FIELD, sw=1.4))

    deploy_box, _, _ = textbox(810, 235, 'Job: deploy-staging\nEphemeral Pod Deploy\n+ Smoke Verification', size=12, bold=True, fill='#f8fafc', stroke=INK, sw=1.6, pad=10)
    frags.append(deploy_box)

    frags.append(arrow(655, 235, 715, 235, color=FIELD, sw=1.8))

    render(os.path.join(IMG, 'runner-dag-execution.svg'), W, H, *frags,
           title='Directed Acyclic Graph (DAG) for Parallel Pipeline Execution')


if __name__ == '__main__':
    fig_pipeline_flow()
    fig_batch_size_lead_time()
    fig_runner_dag()
    print('All figures generated successfully.')
