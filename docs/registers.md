# Register Map

Full register mapping for the VEVOR EML3500-24L inverter. Sourced from the manufacturer documentation [protocol doc](1号通讯协议23年12月1.1版_英语译文_1752730972951.docx).

| Address | Name | Unit | R/W | Description |
| ------- | ---- | ---- | --- | ----------- |
| 100 | Equipment fault code |  | R | 32-bit fault code. Each bit corresponds to a fault code. See the fault code table for details. Fault code 1 corresponds to bit1, fault code 2 corresponds to bit2, and so on. |
| 101 | Equipment fault code |  | R | 32-bit fault code. Each bit corresponds to a fault code. See the fault code table for details. Fault code 1 corresponds to bit1, fault code 2 corresponds to bit2, and so on. |
| 102 | Reserved |  |  | Reserved address |
| 103 | Reserved |  |  | Reserved address |
| 104 | Obtain the warning code for unmasked processing |  |  | The 32-bit warning code is described in the warning code description |
| 105 | Obtain the warning code for unmasked processing |  |  | The 32-bit warning code is described in the warning code description |
| 106 | Reserved |  |  | Reserved address |
| 107 | Reserved |  |  | Reserved address |
| 108 | Obtain the warning code after shield processing |  | R/W | The 32-bit warning code is described in the warning code description |
| 109 | Obtain the warning code after shield processing |  | R/W | The 32-bit warning code is described in the warning code description |
| 110 | Reserved |  |  | Reserved address |
| 111 | Reserved |  |  | Reserved address |
| 112 | Reserved |  |  | Reserved address |
| 113 | Reserved |  |  | Reserved address |
| 114 | Reserved |  |  | Reserved address |
| 115 | Reserved |  |  | Reserved address |
| 116 | Reserved |  |  | Reserved address |
| 117 | Reserved |  |  | Reserved address |
| 118 | Reserved |  |  | Reserved address |
| 119 | Reserved |  |  | Reserved address |
| 120 | Reserved |  |  | Reserved address |
| 121 | Reserved |  |  | Reserved address |
| 122 | Reserved |  |  | Reserved address |
| 123 | Reserved |  |  | Reserved address |
| 124 | Reserved |  |  | Reserved address |
| 125 | Reserved |  |  | Reserved address |
| 126 | Reserved |  |  | Reserved address |
| 127 | Reserved |  |  | Reserved address |
| 128 | Reserved |  |  | Reserved address |
| 129 | Reserved |  |  | Reserved address |
| 130 | Reserved |  |  | Reserved address |
| 131 | Reserved |  |  | Reserved address |
| 132 | Reserved |  |  | Reserved address |
| 133 | Reserved |  |  | Reserved address |
| 134 | Reserved |  |  | Reserved address |
| 135 | Reserved |  |  | Reserved address |
| 136 | Reserved |  |  | Reserved address |
| 137 | Reserved |  |  | Reserved address |
| 138 | Reserved |  |  | Reserved address |
| 139 | Reserved |  |  | Reserved address |
| 140 | Reserved |  |  | Reserved address |
| 141 | Reserved |  |  | Reserved address |
| 142 | Reserved |  |  | Reserved address |
| 143 | Reserved |  |  | Reserved address |
| 144 | Reserved |  |  | Reserved address |
| 145 | Reserved |  |  | Reserved address |
| 146 | Reserved |  |  | Reserved address |
| 147 | Reserved |  |  | Reserved address |
| 148 | Reserved |  |  | Reserved address |
| 149 | Reserved |  |  | Reserved address |
| 150 | Reserved |  |  | Reserved address |
| 151 | Reserved |  |  | Reserved address |
| 152 | Reserved |  |  | Reserved address |
| 153 | Reserved |  |  | Reserved address |
| 154 | Reserved |  |  | Reserved address |
| 155 | Reserved |  |  | Reserved address |
| 156 | Reserved |  |  | Reserved address |
| 157 | Reserved |  |  | Reserved address |
| 158 | Reserved |  |  | Reserved address |
| 159 | Reserved |  |  | Reserved address |
| 160 | Reserved |  |  | Reserved address |
| 161 | Reserved |  |  | Reserved address |
| 162 | Reserved |  |  | Reserved address |
| 163 | Reserved |  |  | Reserved address |
| 164 | Reserved |  |  | Reserved address |
| 165 | Reserved |  |  | Reserved address |
| 166 | Reserved |  |  | Reserved address |
| 167 | Reserved |  |  | Reserved address |
| 168 | Reserved |  |  | Reserved address |
| 169 | Reserved |  |  | Reserved address |
| 170 | Reserved |  |  | Reserved address |
| 171 | Device type |  | R |  |
| 172 | Device name |  | R/W | Device name, written or read in ASCII |
| 173 | Device name |  | R/W | Device name, written or read in ASCII |
| 174 | Device name |  | R/W | Device name, written or read in ASCII |
| 175 | Device name |  | R/W | Device name, written or read in ASCII |
| 176 | Device name |  | R/W | Device name, written or read in ASCII |
| 177 | Device name |  | R/W | Device name, written or read in ASCII |
| 178 | Device name |  | R/W | Device name, written or read in ASCII |
| 179 | Device name |  | R/W | Device name, written or read in ASCII |
| 180 | Device name |  | R/W | Device name, written or read in ASCII |
| 181 | Device name |  | R/W | Device name, written or read in ASCII |
| 182 | Device name |  | R/W | Device name, written or read in ASCII |
| 183 | Device name |  | R/W | Device name, written or read in ASCII |
| 184 | Invalid data |  | R | Agreement number, return 1 for this agreement |
| 185 | Reserved |  |  | Reserved address |
| 186 | Device serial number |  | R |  |
| 187 | Device serial number |  | R |  |
| 188 | Device serial number |  | R |  |
| 189 | Device serial number |  | R |  |
| 190 | Device serial number |  | R |  |
| 191 | Device serial number |  | R |  |
| 192 | Device serial number |  | R |  |
| 193 | Device serial number |  | R |  |
| 194 | Device serial number |  | R |  |
| 195 | Device serial number |  | R |  |
| 196 | Device serial number |  | R |  |
| 197 | Device serial number |  | R |  |
| 198 | Reserved |  |  | Reserved address |
| 199 | Reserved |  |  | Reserved address |
| 200 | Invalid data |  |  | Internal command |
| 201 | Working mode |  | R | 0: Power on mode \| 1: Standby mode \| 2: Mains mode \| 3: Off-grid mode \| 4: Bypass mode \| 5: Charging mode \| 6: Failure Mode |
| 202 | Mains voltage effective value | 0.1v | R |  |
| 203 | Mains frequency | 0.01Hz | R |  |
| 204 | Average mains power | 1w | R |  |
| 205 | Effective value of inverter voltage | 0.1v | R |  |
| 206 | Effective value of inverter current | 0.1A | R |  |
| 207 | Inverter frequency | 0.01Hz | R |  |
| 208 | Inverter power average | 1w | R | Positive indicates inverter output and negative indicates inverter input |
| 209 | Inverter charging power | 1w | R |  |
| 210 | Effective value of output voltage | 0.1v | R |  |
| 211 | Effective value of output current | 0.1A | R |  |
| 212 | Output frequency | 0.01Hz | R |  |
| 213 | Output active power | 1w | R |  |
| 214 | Output apparent power | 1VA | R |  |
| 215 | Average battery voltage | 0.1v | R |  |
| 216 | Average battery current | 0.1A | R |  |
| 217 | Average battery power | 1w | R |  |
| 218 | Invalid data |  |  | Internal command |
| 219 | Average PV voltage | 0.1v | R |  |
| 220 | Average PV current | 0.1A | R |  |
| 221 | Reserved |  |  | Reserved address |
| 222 | Reserved |  |  | Reserved address |
| 223 | Average PV power | 1w | R |  |
| 224 | Average PV charging power | 1w | R |  |
| 225 | Percent of load | 1% | R |  |
| 226 | DCDC temperature | 1℃ | R |  |
| 227 | Inverter temperature | 1℃ | R |  |
| 228 | Reserved |  |  | Reserved address |
| 229 | Battery percentage | 1% | R |  |
| 230 | Invalid data |  |  | Internal command |
| 231 | Power flow status |  | R | See the description of power flow flag bit for details. |
| 232 | Battery current filter average | 0.1A | R | A positive number indicates charging and a negative number indicates discharging. |
| 233 | Average value of inverter charging current | 0.1A | R |  |
| 234 | Average PV charging current | 0.1A | R |  |
| 235 | Invalid data |  |  | Internal command |
| 236 | Invalid data |  |  | Internal command |
| 237 | Reserved |  |  | Reserved address |
| 238 | Reserved |  |  | Reserved address |
| 239 | Reserved |  |  | Reserved address |
| 240 | Reserved |  |  | Reserved address |
| 241 | Reserved |  |  | Reserved address |
| 242 | Reserved |  |  | Reserved address |
| 243 | Reserved |  |  | Reserved address |
| 244 | Reserved |  |  | Reserved address |
| 245 | Reserved |  |  | Reserved address |
| 246 | Reserved |  |  | Reserved address |
| 247 | Reserved |  |  | Reserved address |
| 248 | Reserved |  |  | Reserved address |
| 249 | Reserved |  |  | Reserved address |
| 250 | Reserved |  |  | Reserved address |
| 251 | Reserved |  |  | Reserved address |
| 252 | Reserved |  |  | Reserved address |
| 253 | Reserved |  |  | Reserved address |
| 254 | Reserved |  |  | Reserved address |
| 255 | Reserved |  |  | Reserved address |
| 256 | Reserved |  |  | Reserved address |
| 257 | Reserved |  |  | Reserved address |
| 258 | Reserved |  |  | Reserved address |
| 259 | Reserved |  |  | Reserved address |
| 260 | Reserved |  |  | Reserved address |
| 261 | Reserved |  |  | Reserved address |
| 262 | Reserved |  |  | Reserved address |
| 263 | Reserved |  |  | Reserved address |
| 264 | Reserved |  |  | Reserved address |
| 265 | Reserved |  |  | Reserved address |
| 266 | Reserved |  |  | Reserved address |
| 267 | Reserved |  |  | Reserved address |
| 268 | Reserved |  |  | Reserved address |
| 269 | Reserved |  |  | Reserved address |
| 270 | Reserved |  |  | Reserved address |
| 271 | Reserved |  |  | Reserved address |
| 272 | Reserved |  |  | Reserved address |
| 273 | Reserved |  |  | Reserved address |
| 274 | Reserved |  |  | Reserved address |
| 275 | Reserved |  |  | Reserved address |
| 276 | Reserved |  |  | Reserved address |
| 277 | Reserved |  |  | Reserved address |
| 278 | Reserved |  |  | Reserved address |
| 279 | Reserved |  |  | Reserved address |
| 280 | Reserved |  |  | Reserved address |
| 281 | Reserved |  |  | Reserved address |
| 282 | Reserved |  |  | Reserved address |
| 283 | Reserved |  |  | Reserved address |
| 284 | Reserved |  |  | Reserved address |
| 285 | Reserved |  |  | Reserved address |
| 286 | Reserved |  |  | Reserved address |
| 287 | Reserved |  |  | Reserved address |
| 288 | Reserved |  |  | Reserved address |
| 289 | Reserved |  |  | Reserved address |
| 290 | Reserved |  |  | Reserved address |
| 291 | Reserved |  |  | Reserved address |
| 292 | Reserved |  |  | Reserved address |
| 293 | Reserved |  |  | Reserved address |
| 294 | Reserved |  |  | Reserved address |
| 295 | Reserved |  |  | Reserved address |
| 296 | Reserved |  |  | Reserved address |
| 297 | Reserved |  |  | Reserved address |
| 298 | Reserved |  |  | Reserved address |
| 299 | Reserved |  |  | Reserved address |
| 300 | Output mode |  | R/W | 0: single machine; \| 1: parallel; \| 2: Three-phase combination-P1 \| 3: Three-phase combination-P2 \| 4: Three-phase combination-P3 |
| 301 | Output priority |  | R/W | 0: Main-PV-Battery (UTI) \| 1: PV-mains-battery (SOL) [priority inverter] \| 2: PV-battery-mains (SBU) \| 3: PV-Mains-Battery (SUB) [Priority Mains] |
| 302 | Input voltage range |  | R/W | 0：APL； \| 1：UPS； |
| 303 | Buzzer mode |  | R/W | 0: mute in all cases; \| 1: Sound when the input source changes or there is a specific warning or fault; 2: Sound when there is a specific warning or fault; \| 3: Sound in case of fault; |
| 304 | Reserved |  | R/W | Reserved address |
| 305 | LCD backlight |  | R/W | 0: Timed closing; \| 1: Always on; |
| 306 | LCD automatically returns to the home page |  | R/W | 0: Do not return automatically; \| 1: Automatic return after 1 minute; |
| 307 | Energy saving mode switch |  | R/W | 0: Energy saving mode off; \| 1: Energy-saving mode on; |
| 308 | Overload automatic restart |  | R/W | 0: Overload failure does not restart; \| 1: Automatic restart in case of overload; |
| 309 | Over-temperature automatic restart |  | R/W | 0: No restart for over-temperature fault; \| 1: Automatic restart for over-temperature fault; |
| 310 | Overload Bypass Enable |  | R/W | 0: forbidden; \| 1: Enable; |
| 311 | Reserved |  |  | Reserved address |
| 312 | Reserved |  |  | Reserved address |
| 313 | Battery Eq Mode Enable |  | R/W | 0: forbidden; \| 1: Enable; |
| 314 | Warning Mask [I] |  | R/W | The warning corresponding to 1 is normally displayed, and the warning corresponding to 0 is shielded. |
| 315 | Warning Mask [I] |  | R/W | The warning corresponding to 1 is normally displayed, and the warning corresponding to 0 is shielded. |
| 316 | Dry contact |  | R/W | 0: normal mode; \| 1: Grounding box mode; |
| 317 | Reserved |  |  | Reserved address |
| 318 | Reserved |  |  | Reserved address |
| 319 | Reserved |  |  | Reserved address |
| 320 | Output voltage | 0.1v | R/W | 2200: 220V output; \| 2300: 230v output; \| 2400: 240v output; |
| 321 | Output frequency | 0.01Hz | R/W | 5000: 50Hz output; \| 6000: 60Hz output; |
| 322 | Battery type |  | R/W | 0：AGM； \| 1：FLD； \| 2：USER； \| 3：Li1 \| 4：Li2 \| 5：Li3 \| 6：Li4 |
| 323 | Battery overvoltage protection point [A] | 0.1v | R/W | Range: (B + 1V * J) ~ 16.5v * J |
| 324 | Maximum charge voltage [B] | 0.1v | R/W | Range: C ~ (A-1v) |
| 325 | Floating charge voltage \| [C] | 0.1v | R/W | Range: (12v * J) ~ B |
| 326 | Mains mode battery discharge recovery point [D] | 0.1v | R/W | Range: (B-0.5V * J) ~ Max (12V * J, E) \| Set to 0 to indicate a full recovery |
| 327 | Battery low voltage protection point in mains mode [E] | 0.1v | R/W | Range: Min (14.3v * J, D) ~ Max (11v * J, F) |
| 328 | Reserved |  |  | Reserved address |
| 329 | Off-grid mode battery low voltage protection point [F] | 0.1v | R/W | Range: (10v * J) ~ Min (13.5v * J, E) |
| 330 | Waiting time from constant voltage to floating charge | min | R/W | Range: 1 ~ 900 min \| Set to 0 to default to 10 min |
| 331 | Battery charging priority |  | R/W | 0: mains supply is preferred; \| 1: PV priority; \| 2: PV is at the same level as mains supply; \| 3: PV charging only allowed |
| 332 | Maximum charge current [G] | 0.1A | R/W | Range: Max (10 A, H) ~ 80 A |
| 333 | Maximum mains charging current [H] | 0.1A | R/W | Range: 2A ~ G |
| 334 | The charging voltage of Eq | 0.1v | R/W | Range: C ~ (A-0.5v * J)http://c/ |
| 335 | bat_eq_time | min | R/W | Range: 0 ~ 900 |
| 336 | Eq timed out | min | R/W | Range: 0 ~ 900 |
| 337 | Two-time Eq charge interval | day | R/W | Range: 1 ~ 90 |
| 338 | Automatic Mains Output Enable |  | R/W | 0: No mains power output without pressing the power button 1: Automatic mains power output without pressing the power button |
| 339 | Reserved |  |  | Reserved address |
| 340 | Reserved |  |  | Reserved address |
| 341 | Mains mode battery discharge SOC protection value [K] | 1% | R/W | Range: 20% ~ 50% |
| 342 | Mains mode battery discharge SOC recovery value | 1% | R/W | Range: 60% ~ 100% |
| 343 | Battery discharge SOC protection value in off-grid mode | 1% | R/W | Range: 3% ~ Min (K, 30%) |
| 344 | Reserved |  |  |  |
| 345 | Reserved |  |  |  |
| 346 | Reserved |  |  |  |
| 347 | Reserved |  |  |  |
| 348 | Reserved |  |  |  |
| 349 | Reserved |  |  |  |
| 350 | Reserved |  |  |  |
| 351 | Maximum discharge current protection | 1A | R/W | Maximum discharge current protection value in stand-alone mode |
| 352 | Reserved |  |  |  |
| 353 | Reserved |  |  |  |
| 354 | Reserved |  |  |  |
| 355 | Reserved |  |  |  |
| 356 | Reserved |  |  |  |
| 357 | Reserved |  |  |  |
| 358 | Reserved |  |  |  |
| 359 | Reserved |  |  |  |
| 360 | Reserved |  |  |  |
| 361 | Reserved |  |  |  |
| 362 | Reserved |  |  |  |
| 363 | Reserved |  |  |  |
| 364 | Reserved |  |  |  |
| 365 | Reserved |  |  |  |
| 366 | Reserved |  |  |  |
| 367 | Reserved |  |  |  |
| 368 | Reserved |  |  |  |
| 369 | Reserved |  |  |  |
| 370 | Reserved |  |  |  |
| 371 | Reserved |  |  |  |
| 372 | Reserved |  |  |  |
| 373 | Reserved |  |  |  |
| 374 | Reserved |  |  |  |
| 375 | Reserved |  |  |  |
| 376 | Reserved |  |  |  |
| 377 | Reserved |  |  |  |
| 378 | Reserved |  |  |  |
| 379 | Reserved |  |  |  |
| 380 | Reserved |  |  |  |
| 381 | Reserved |  |  |  |
| 382 | Reserved |  |  |  |
| 383 | Reserved |  |  |  |
| 384 | Reserved |  |  |  |
| 385 | Reserved |  |  |  |
| 386 | Reserved |  |  |  |
| 387 | Reserved |  |  |  |
| 388 | Reserved |  |  |  |
| 389 | Reserved |  |  |  |
| 390 | Reserved |  |  |  |
| 391 | Reserved |  |  |  |
| 392 | Reserved |  |  |  |
| 393 | Reserved |  |  |  |
| 394 | Reserved |  |  |  |
| 395 | Reserved |  |  |  |
| 396 | Reserved |  |  |  |
| 397 | Reserved |  |  |  |
| 398 | Reserved |  |  |  |
| 399 | Reserved |  |  |  |
| 400 | Reserved |  |  |  |
| 401 | Reserved |  |  |  |
| 402 | Reserved |  |  |  |
| 403 | Reserved |  |  |  |
| 404 | Reserved |  |  |  |
| 405 | Reserved |  |  |  |
| 406 | Boot mode |  | R/W | 0: Can be powered on locally or remotely \| 1: Only local boot \| 2: Remote boot only |
| 407 | Reserved |  |  | Reserved address |
| 408 | Reserved |  |  | Reserved address |
| 409 | Reserved |  |  | Reserved address |
| 410 | Reserved |  |  | Reserved address |
| 411 | Reserved |  |  | Reserved address |
| 412 | Reserved |  |  | Reserved address |
| 413 | Reserved |  |  | Reserved address |
| 414 | Reserved |  |  | Reserved address |
| 415 | Reserved |  |  | Reserved address |
| 416 | Reserved |  |  | Reserved address |
| 417 | Reserved |  |  | Reserved address |
| 418 | Reserved |  |  | Reserved address |
| 419 | Reserved |  |  | Reserved address |
| 420 | Remote switch |  | R/W | 0: Remote shutdown \| 1: Remote power-on |
| 421 | Invalid data |  |  | Internal command |
| 422 | Reserved |  |  | Reserved address |
| 423 | Reserved |  |  | Reserved address |
| 424 | Reserved |  |  | Reserved address |
| 425 | Forcing the charge of Eq |  | W | 1: Manually force Eq to charge once |
| 426 | Exits the fail-locked state |  | W | 1: Exit the fault lock state (it will take effect only when the machine enters the fault mode) |
| 427 | Invalid data |  |  | Internal command |
| 428 | Reserved |  |  | Reserved address |
| 429 | Reserved |  |  | Reserved address |
| 430 | Reserved |  |  | Reserved address |
| 431 | Reserved |  |  | Reserved address |
| 432 | Reserved |  |  | Reserved address |
| 433 | Reserved |  |  | Reserved address |
| 434 | Reserved |  |  | Reserved address |
| 435 | Reserved |  |  | Reserved address |
| 436 | Reserved |  |  | Reserved address |
| 437 | Reserved |  |  | Reserved address |
| 438 | Reserved |  |  | Reserved address |
| 439 | Reserved |  |  | Reserved address |
| 440 | Reserved |  |  | Reserved address |
| 441 | Reserved |  |  | Reserved address |
| 442 | Reserved |  |  | Reserved address |
| 443 | Reserved |  |  | Reserved address |
| 444 | Reserved |  |  | Reserved address |
| 445 | Reserved |  |  | Reserved address |
| 446 | Reserved |  |  | Reserved address |
| 447 | Reserved |  |  | Reserved address |
| 448 | Reserved |  |  | Reserved address |
| 449 | Reserved |  |  | Reserved address |
| 450 | Invalid data |  |  | Internal command |
| 451 | Invalid data |  |  | Internal command |
| 452 | Invalid data |  |  | Internal command |
| 453 | Invalid data |  |  | Internal command |
| 454 | Invalid data |  |  | Internal command |
| 455 | Invalid data |  |  | Internal command |
| 456 | Invalid data |  |  | Internal command |
| 457 | Reserved |  |  | Reserved address |
| 458 | Reserved |  |  | Reserved address |
| 459 | Reserved |  |  | Reserved address |
| 460 | Clear the record |  | W | 0 xAA: clear the operation record and fault record (effective in non-off-grid mode) |
| 461 | Reset user parameters |  | W | 0 xAA: User parameters are restored to default values (works in non-off-grid mode) |
| 462 | Invalid data |  |  | Internal command |
| 463 | Invalid data |  |  | Internal command |
| 464 | Invalid data |  |  | Internal command |
| 465 | Invalid data |  |  | Internal command |
| 466 | Invalid data |  |  | Internal command |
| 467 | Invalid data |  |  | Internal command |
| 468 | Reserved |  |  | Reserved address |
| 469 | Reserved |  |  | Reserved address |
| 470 | Reserved |  |  | Reserved address |
| 471 | Reserved |  |  | Reserved address |
| 472 | Reserved |  |  | Reserved address |
| 473 | Reserved |  |  | Reserved address |
| 474 | Reserved |  |  | Reserved address |
| 475 | Reserved |  |  | Reserved address |
| 476 | Reserved |  |  | Reserved address |
| 477 | Reserved |  |  | Reserved address |
| 478 | Reserved |  |  | Reserved address |
| 479 | Reserved |  |  | Reserved address |
| 480 | Reserved |  |  | Reserved address |
| 481 | Reserved |  |  | Reserved address |
| 482 | Reserved |  |  | Reserved address |
| 483 | Reserved |  |  | Reserved address |
| 484 | Reserved |  |  | Reserved address |
| 485 | Reserved |  |  | Reserved address |
| 486 | Reserved |  |  | Reserved address |
| 487 | Reserved |  |  | Reserved address |
| 488 | Reserved |  |  | Reserved address |
| 489 | Reserved |  |  | Reserved address |
| 490 | Reserved |  |  | Reserved address |
| 491 | Reserved |  |  | Reserved address |
| 492 | Reserved |  |  | Reserved address |
| 493 | Reserved |  |  | Reserved address |
| 494 | Reserved |  |  | Reserved address |
| 495 | Reserved |  |  | Reserved address |
| 496 | Reserved |  |  | Reserved address |
| 497 | Reserved |  |  | Reserved address |
| 498 | Reserved |  |  | Reserved address |
| 499 | Reserved |  |  | Reserved address |
| 500 | Invalid data |  |  | Internal command |
| 501 | Invalid data |  |  | Internal command |
| 502 | Invalid data |  |  | Internal command |
| 503 | Invalid data |  |  | Internal command |
| 504 | Invalid data |  |  | Internal command |
| 505 | Invalid data |  |  | Internal command |
| 506 | Invalid data |  |  | Internal command |
| 507 | Invalid data |  |  | Internal command |
| 508 | Invalid data |  |  | Internal command |
| 509 | Invalid data |  |  | Internal command |
| 510 | Invalid data |  |  | Internal command |
| 511 | Invalid data |  |  | Internal command |
| 512 | Invalid data |  |  | Internal command |
| 513 | Invalid data |  |  | Internal command |
| 514 | Invalid data |  |  | Internal command |
| 515 | Invalid data |  |  | Internal command |
| 516 | Invalid data |  |  | Internal command |
| 517 | Invalid data |  |  | Internal command |
| 518 | Invalid data |  |  | Internal command |
| 519 | Invalid data |  |  | Internal command |
| 520 | Invalid data |  |  | Internal command |
| 521 | Invalid data |  |  | Internal command |
| 522 | Invalid data |  |  | Internal command |
| 523 | Invalid data |  |  | Internal command |
| 524 | Invalid data |  |  | Internal command |
| 525 | Invalid data |  |  | Internal command |
| 526 | Invalid data |  |  | Internal command |
| 527 | Invalid data |  |  | Internal command |
| 528 | Invalid data |  |  | Internal command |
| 529 | Invalid data |  |  | Internal command |
| 530 | Invalid data |  |  | Internal command |
| 531 | Invalid data |  |  | Internal command |
| 532 | Invalid data |  |  | Internal command |
| 533 | Invalid data |  |  | Internal command |
| 534 | Reserved |  |  | Reserved address |
| 535 | Reserved |  |  | Reserved address |
| 536 | Reserved |  |  | Reserved address |
| 537 | Reserved |  |  | Reserved address |
| 538 | Reserved |  |  | Reserved address |
| 539 | Reserved |  |  | Reserved address |
| 540 | Reserved |  |  | Reserved address |
| 541 | Reserved |  |  | Reserved address |
| 542 | Reserved |  |  | Reserved address |
| 543 | Reserved |  |  | Reserved address |
| 544 | Reserved |  |  | Reserved address |
| 545 | Reserved |  |  | Reserved address |
| 546 | Reserved |  |  | Reserved address |
| 547 | Reserved |  |  | Reserved address |
| 548 | Reserved |  |  | Reserved address |
| 549 | Reserved |  |  | Reserved address |
| 550 | Reserved |  |  | Reserved address |
| 551 | Reserved |  |  | Reserved address |
| 552 | Reserved |  |  | Reserved address |
| 553 | Reserved |  |  | Reserved address |
| 554 | Reserved |  |  | Reserved address |
| 555 | Reserved |  |  | Reserved address |
| 556 | Reserved |  |  | Reserved address |
| 557 | Reserved |  |  | Reserved address |
| 558 | Reserved |  |  | Reserved address |
| 559 | Reserved |  |  | Reserved address |
| 560 | Reserved |  |  | Reserved address |
| 561 | Reserved |  |  | Reserved address |
| 562 | Reserved |  |  | Reserved address |
| 563 | Reserved |  |  | Reserved address |
| 564 | Reserved |  |  | Reserved address |
| 565 | Reserved |  |  | Reserved address |
| 566 | Reserved |  |  | Reserved address |
| 567 | Reserved |  |  | Reserved address |
| 568 | Reserved |  |  | Reserved address |
| 569 | Reserved |  |  | Reserved address |
| 570 | Reserved |  |  | Reserved address |
| 571 | Reserved |  |  | Reserved address |
| 572 | Reserved |  |  | Reserved address |
| 573 | Reserved |  |  | Reserved address |
| 574 | Reserved |  |  | Reserved address |
| 575 | Reserved |  |  | Reserved address |
| 576 | Reserved |  |  | Reserved address |
| 577 | Reserved |  |  | Reserved address |
| 578 | Reserved |  |  | Reserved address |
| 579 | Reserved |  |  | Reserved address |
| 580 | Reserved |  |  | Reserved address |
| 581 | Reserved |  |  | Reserved address |
| 582 | Reserved |  |  | Reserved address |
| 583 | Reserved |  |  | Reserved address |
| 584 | Reserved |  |  | Reserved address |
| 585 | Reserved |  |  | Reserved address |
| 586 | Reserved |  |  | Reserved address |
| 587 | Reserved |  |  | Reserved address |
| 588 | Reserved |  |  | Reserved address |
| 589 | Reserved |  |  | Reserved address |
| 590 | Reserved |  |  | Reserved address |
| 591 | Reserved |  |  | Reserved address |
| 592 | Reserved |  |  | Reserved address |
| 593 | Reserved |  |  | Reserved address |
| 594 | Reserved |  |  | Reserved address |
| 595 | Reserved |  |  | Reserved address |
| 596 | Reserved |  |  | Reserved address |
| 597 | Reserved |  |  | Reserved address |
| 598 | Reserved |  |  | Reserved address |
| 599 | Reserved |  |  | Reserved address |
| 600 | Invalid data |  |  | Internal command |
| 601 | Invalid data |  |  | Internal command |
| 602 | Invalid data |  |  | Internal command |
| 603 | Invalid data |  |  | Internal command |
| 604 | Invalid data |  |  | Internal command |
| 605 | Invalid data |  |  | Internal command |
| 606 | Invalid data |  |  | Internal command |
| 607 | Invalid data |  |  | Internal command |
| 608 | Invalid data |  |  | Internal command |
| 609 | Invalid data |  |  | Internal command |
| 610 | Invalid data |  |  | Internal command |
| 611 | Invalid data |  |  | Internal command |
| 612 | Invalid data |  |  | Internal command |
| 613 | Invalid data |  |  | Internal command |
| 614 | Invalid data |  |  | Internal command |
| 615 | Invalid data |  |  | Internal command |
| 616 | Invalid data |  |  | Internal command |
| 617 | Invalid data |  |  | Internal command |
| 618 | Invalid data |  |  | Internal command |
| 619 | Invalid data |  |  | Internal command |
| 620 | Invalid data |  |  | Internal command |
| 621 | Invalid data |  |  | Internal command |
| 622 | Invalid data |  |  | Internal command |
| 623 | Invalid data |  |  | Internal command |
| 624 | Invalid data |  |  | Internal command |
| 625 | Invalid data |  |  | Internal command |
| 626 | Program version |  | R |  |
| 626 | Invalid data |  |  | Internal command |
| 627 | Program version |  | R |  |
| 627 | Invalid data |  |  | Internal command |
| 628 | Program version |  | R |  |
| 628 | Invalid data |  |  | Internal command |
| 629 | Program version |  | R |  |
| 629 | Invalid data |  |  | Internal command |
| 630 | Program version |  | R |  |
| 630 | Invalid data |  |  | Internal command |
| 631 | Program version |  | R |  |
| 631 | Invalid data |  |  | Internal command |
| 632 | Program version |  | R |  |
| 632 | Invalid data |  |  | Internal command |
| 633 | Program version |  | R |  |
| 633 | Invalid data |  |  | Internal command |
| 634 | Reserved |  |  | Reserved address |
| 635 | Reserved |  |  | Reserved address |
| 636 | Reserved |  |  | Reserved address |
| 637 | Reserved |  |  | Reserved address |
| 638 | Reserved |  |  | Reserved address |
| 639 | Reserved |  |  | Reserved address |
| 640 | Reserved |  |  | Reserved address |
| 643 | Rated power | w | R |  |
| 644 | Rated number of cells [J] | PCS | R |  |
| 645 | Reserved |  |  | Reserved address |
| 646 | Reserved |  |  | Reserved address |
| 647 | Reserved |  |  | Reserved address |
| 648 | Reserved |  |  | Reserved address |
| 649 | Reserved |  |  | Reserved address |
| 650 | Reserved |  |  | Reserved address |
| 651 | Reserved |  |  | Reserved address |
| 652 | Reserved |  |  | Reserved address |
| 653 | Reserved |  |  | Reserved address |
| 654 | Reserved |  |  | Reserved address |
| 655 | Reserved |  |  | Reserved address |
| 656 | Reserved |  |  | Reserved address |
| 657 | Reserved |  |  | Reserved address |
| 658 | Reserved |  |  | Reserved address |
| 659 | Reserved |  |  | Reserved address |
| 660 | Reserved |  |  | Reserved address |
| 661 | Reserved |  |  | Reserved address |
| 662 | Reserved |  |  | Reserved address |
| 663 | Reserved |  |  | Reserved address |
| 664 | Reserved |  |  | Reserved address |
| 665 | Reserved |  |  | Reserved address |
| 666 | Reserved |  |  | Reserved address |
| 667 | Reserved |  |  | Reserved address |
| 668 | Reserved |  |  | Reserved address |
| 669 | Reserved |  |  | Reserved address |
| 670 | Reserved |  |  | Reserved address |
| 671 | Reserved |  |  | Reserved address |
| 672 | Reserved |  |  | Reserved address |
| 673 | Reserved |  |  | Reserved address |
| 674 | Reserved |  |  | Reserved address |
| 675 | Reserved |  |  | Reserved address |
| 676 | Reserved |  |  | Reserved address |
| 677 | Reserved |  |  | Reserved address |
| 678 | Reserved |  |  | Reserved address |
| 679 | Reserved |  |  | Reserved address |
| 680 | Reserved |  |  | Reserved address |
| 681 | Reserved |  |  | Reserved address |
| 682 | Reserved |  |  | Reserved address |
| 683 | Reserved |  |  | Reserved address |
| 684 | Reserved |  |  | Reserved address |
| 685 | Reserved |  |  | Reserved address |
| 686 | Reserved |  |  | Reserved address |
| 687 | Reserved |  |  | Reserved address |
| 688 | Reserved |  |  | Reserved address |
| 689 | Reserved |  |  | Reserved address |
| 690 | Reserved |  |  | Reserved address |
| 691 | Reserved |  |  | Reserved address |
| 692 | Reserved |  |  | Reserved address |
| 693 | Reserved |  |  | Reserved address |
| 694 | Reserved |  |  | Reserved address |
| 695 | Reserved |  |  | Reserved address |
| 696 | Reserved |  |  | Reserved address |
| 697 | Reserved |  |  | Reserved address |
| 698 | Reserved |  |  | Reserved address |
| 699 | Reserved |  |  | Reserved address |
| 700 | Fault record storage information [K] |  | R | Upper 16 bits: the position of the latest record; \| Lower 16 bits: total number of existing fault messages |
| 701 | Fault record storage information [K] |  | R | Upper 16 bits: the position of the latest record; \| Lower 16 bits: total number of existing fault messages |
| 702 | Fault Information Query Index |  | R/W | Set the fault information index to be queried, range: 0 ~ total number of existing fault information |
| 703 | Fault Record [M] |  | R | See the fault record format for details. |
| 704 | Fault Record [M] |  | R | See the fault record format for details. |
| 705 | Fault Record [M] |  | R | See the fault record format for details. |
| 706 | Fault Record [M] |  | R | See the fault record format for details. |
| 707 | Fault Record [M] |  | R | See the fault record format for details. |
| 708 | Fault Record [M] |  | R | See the fault record format for details. |
| 709 | Fault Record [M] |  | R | See the fault record format for details. |
| 710 | Fault Record [M] |  | R | See the fault record format for details. |
| 711 | Fault Record [M] |  | R | See the fault record format for details. |
| 712 | Fault Record [M] |  | R | See the fault record format for details. |
| 713 | Fault Record [M] |  | R | See the fault record format for details. |
| 714 | Fault Record [M] |  | R | See the fault record format for details. |
| 715 | Fault Record [M] |  | R | See the fault record format for details. |
| 716 | Fault Record [M] |  | R | See the fault record format for details. |
| 717 | Fault Record [M] |  | R | See the fault record format for details. |
| 718 | Fault Record [M] |  | R | See the fault record format for details. |
| 719 | Fault Record [M] |  | R | See the fault record format for details. |
| 720 | Fault Record [M] |  | R | See the fault record format for details. |
| 721 | Fault Record [M] |  | R | See the fault record format for details. |
| 722 | Fault Record [M] |  | R | See the fault record format for details. |
| 723 | Fault Record [M] |  | R | See the fault record format for details. |
| 724 | Fault Record [M] |  | R | See the fault record format for details. |
| 725 | Fault Record [M] |  | R | See the fault record format for details. |
| 726 | Fault Record [M] |  | R | See the fault record format for details. |
| 727 | Fault Record [M] |  | R | See the fault record format for details. |
| 728 | Fault Record [M] |  | R | See the fault record format for details. |
| 729 | Run the log |  | R | See the operation log description for details |
| 730 | Run the log |  | R | See the operation log description for details |
| 731 | Run the log |  | R | See the operation log description for details |
| 732 | Run the log |  | R | See the operation log description for details |
| 733 | Run the log |  | R | See the operation log description for details |
| 734 | Run the log |  | R | See the operation log description for details |
| 735 | Run the log |  | R | See the operation log description for details |
| 736 | Run the log |  | R | See the operation log description for details |
| 737 | Run the log |  | R | See the operation log description for details |
| 738 | Run the log |  | R | See the operation log description for details |
| 739 | Run the log |  | R | See the operation log description for details |
| 740 | Run the log |  | R | See the operation log description for details |
| 741 | Run the log |  | R | See the operation log description for details |
| 742 | Run the log |  | R | See the operation log description for details |
| 743 | Run the log |  | R | See the operation log description for details |
| 744 | Run the log |  | R | See the operation log description for details |
| 745 | Reserved |  |  | Reserved address |
| 746 | Reserved |  |  | Reserved address |
| 747 | Reserved |  |  | Reserved address |
| 748 | Reserved |  |  | Reserved address |
| 749 | Reserved |  |  | Reserved address |