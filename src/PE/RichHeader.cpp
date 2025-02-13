/* Copyright 2017 - 2022 R. Thomas
 * Copyright 2017 - 2022 Quarkslab
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
#include <iomanip>

#include "LIEF/PE/hash.hpp"

#include "LIEF/PE/RichHeader.hpp"

namespace LIEF {
namespace PE {

RichHeader::~RichHeader() = default;
RichHeader::RichHeader(const RichHeader&) = default;
RichHeader& RichHeader::operator=(const RichHeader&) = default;

RichHeader::RichHeader() = default;

uint32_t RichHeader::key() const {
  return key_;
}

RichHeader::it_entries RichHeader::entries() {
  return entries_;
}

RichHeader::it_const_entries RichHeader::entries() const {
  return entries_;
}

void RichHeader::key(uint32_t key) {
  key_ = key;
}

void RichHeader::add_entry(const RichEntry& entry) {
  entries_.push_back(entry);
}

void RichHeader::add_entry(uint16_t id, uint16_t build_id, uint32_t count) {
  entries_.emplace_back(id, build_id, count);
}

void RichHeader::accept(LIEF::Visitor& visitor) const {
  visitor.visit(*this);
}

bool RichHeader::operator==(const RichHeader& rhs) const {
  if (this == &rhs) {
    return true;
  }
  size_t hash_lhs = Hash::hash(*this);
  size_t hash_rhs = Hash::hash(rhs);
  return hash_lhs == hash_rhs;
}

bool RichHeader::operator!=(const RichHeader& rhs) const {
  return !(*this == rhs);
}


std::ostream& operator<<(std::ostream& os, const RichHeader& rich_header) {
  os << "Key: " << std::hex << rich_header.key() << std::endl;
  for (const RichEntry& entry : rich_header.entries()) {
    os << "  - " << entry << std::endl;
  }
  return os;
}

}
}
