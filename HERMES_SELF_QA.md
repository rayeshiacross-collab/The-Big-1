# Hermes self-quality check — required production gate

Owner instruction: Hermes must check its own work before calling it complete. A completed YouTube video means the full exported video and upload package have passed review, not only script validation or sample frames.

## Writing review

After producing the final files, Hermes must reread the narration, verify factual claims against sources, remove unresolved VERIFY flags, check completeness and confirm that every scene conveys its narration. Unsupported psychology diagnoses or certainty about another person's motives must be corrected. Preserve the exact approved narration unless a revision is explicitly recorded.

Save a dated review for the stable content ID, with reviewer Hermes, stage writing, actual artifact SHA-256 values, verdict PASS/FAIL, unresolved_issues and checks for accuracy, completeness and scene_alignment. Each check needs status and concrete evidence. A checklist copied from instructions is not evidence. Failed checks require correction and another review.

`mark_complete(..., self_qa_report=report)` rejects absent/stale/wrong-content/failed reviews before appending WRITING_COMPLETE. It also retains the review identity and hashes in the ledger. Tests use synthetic review fixtures; those fixtures are never production approvals.

## Finished-video review

Hermes must watch the whole final MP4 and listen to all audio using tools capable of doing so. If those capabilities are unavailable, record NOT_REVIEWED and stop; never infer a full playback pass from frames, text or a technical probe.

For stage video, provide checks and evidence for:

- narration: exact words, approved project voice, clear pronunciation, natural delivery and complete beginning/end;
- visible_action: actual subjects/objects perform the scripted actions and convey the spoken meaning; no black-text or still-panel substitute;
- captions: source wording, spelling, readable contrast/safe placement and actual timing;
- timing: every scene matches narration, cuts make sense, no accidental frozen spans or padding;
- sound: intelligible speech, balanced levels, no clipping, missing lines or abrupt truncation;
- continuity: consistent style, object/hand integrity and no accidental visual contradictions;
- technical_export: full decode and stream probe, expected dimensions, orientation, duration and usable audio/video tracks;
- thumbnail: matching content, clear focal point, readable at small sizes;
- youtube_metadata: correct title, description, captions, keywords and appropriate AI/audience/promotion settings, without unsupported claims.

Evidence should identify timestamps/segments, observations and actual technical measurements or artifact paths as appropriate. Set watched_full_video and listened_full_audio only after complete playback review. Hash the exact final MP4, thumbnail, captions and metadata package. Re-exporting or changing any file invalidates its old review.

`src.self_qa.require_self_qa(..., stage='video')` validates the receipt structure, artifact hashes, all nine checks and both full-playback attestations. It does not perform perception, authenticate the reviewer or guarantee honest evidence. The renderer/publisher integration must call it before accepting a final video. This hub still rejects VIDEO_QA_PASSED/RELEASE_APPROVED transitions until those integrations exist; this document does not enable them.

Save defects, fixes, new hashes and the final report with the project ledger. A self-QA pass never sets human release approval or publishes anything. If a scene or check fails, fix it and repeat review of the affected material and final assembled video.

Current state: these gates are part of the open hardening PR. No Hermes runtime, finished-video review or public release is claimed by adding this policy.
